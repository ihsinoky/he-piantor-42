#include "autoroute2/session.h"

#include "board/RoutingBoard.h"
#include "board/Components.h"
#include "board/Item.h"
#include "board/Pin.h"
#include "board/Via.h"
#include "board/DrillItem.h"
#include "geometry/planar/Circle.h"
#include "board/PolylineTrace.h"
#include "board/Trace.h"
#include "board/ObstacleArea.h"
#include "board/ViaObstacleArea.h"
#include "board/ComponentObstacleArea.h"
#include "board/ConductionArea.h"
#include "board/BoardOutline.h"
#include "board/ComponentOutline.h"
#include "board/FixedState.h"
#include "board/ForcedViaAlgo.h"
#include "board/TestLevel.h"
#include "geometry/planar/ConvexShape.h"
#include "board/AngleRestriction.h"
#include "datastructures/UndoableObjects.h"
#include "geometry/planar/IntPoint.h"
#include "geometry/planar/IntBox.h"
#include "geometry/planar/Polyline.h"
#include "geometry/planar/Point.h"
#include "geometry/planar/FloatPoint.h"
#include "rules/BoardRules.h"
#include "rules/ClearanceMatrix.h"
#include "rules/Net.h"
#include "rules/Nets.h"
#include "rules/NetClass.h"
#include "rules/ViaRule.h"
#include "rules/ViaInfo.h"
#include "library/Padstack.h"
#include "interactive/BoardHandling.h"
#include "interactive/ScreenMessages.h"
#include "interactive/InteractiveActionThread.h"
#include "interactive/Settings.h"
#include "interactive/AutorouteSettings.h"
#include "autoroute/AutorouteControl.h"

#include <algorithm>
#include <set>
#include <atomic>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <functional>
#include <iostream>
#include <limits>
#include <map>
#include <memory>
#include <queue>
#include <unordered_map>
#include <unordered_set>
#include <vector>

namespace autoroute2 {
namespace {

struct IBox {
    int32_t x0 = 0, y0 = 0, x1 = 0, y1 = 0;
};

struct IPt {
    int32_t x = 0, y = 0;
};

enum class Kind { Other, Pin, Via, Trace, Keepout, ViaKeepout, Plane };

struct SnapItem {
    board::Item* item = nullptr;
    Kind kind = Kind::Other;
    int net = 0;
    int layer0 = 0;
    int layer1 = 0;
    int clearance = 0;
    bool fixed = false;
    bool hard = false;
    IBox box;
    IPt center;
    std::vector<IPt> corners;
    int component = -1;
};

struct Snap {
    board::RoutingBoard* board = nullptr;
    int32_t bx0 = 0, by0 = 0, bx1 = 0, by1 = 0;
    int layers = 1;
    int angle = 0;
    bool vias_allowed = true;
    int via_cost = 100;
    int ripup_cost = 100;
    // replaces the start ripup costs of the settings while the optimizer reroutes one item
    int ripup_start = 0;
    bool ripup = true;
    bool fanout = false;
    int half_w = 50;
    std::vector<char> forbid_rip;
    std::vector<double> rip_cost;
    int clearance = 50;
    int via_r = 50;
    library::Padstack* via_pad = nullptr;
    int via_clearance = 0;
    int generation = 0;
    int version = 0;
    bool has_outline = false;
    bool flat_dir = false;
    int edge_cl = 0;
    std::vector<std::vector<IPt>> outline;
    std::vector<char> layer_on;
    std::vector<SnapItem> items;
    std::vector<double> cost_h;
    std::vector<double> cost_v;
};

struct Room {
    int layer = 0;
    IBox box;
    int rip_item = -1;
    bool start = false;
    bool dest = false;
    bool has_goal = false;
    IPt goal{};
    IPt goal_entry{};
    int64_t goal_d = std::numeric_limits<int64_t>::max();
    bool has_start = false;
    IPt start_at{};
    IPt start_entry{};
    int64_t start_d = std::numeric_limits<int64_t>::max();
};

struct Section {
    bool occupied = false;
    int back_door = -1;
    int back_sec = -1;
    bool ripped = false;
    int8_t adjust = 0;
    int rip_item = -1;
    IPt at;
    IPt mid;
    int32_t lo = 0;
    int32_t hi = 0;
};

struct Door {
    int room_a = -1;
    int room_b = -1;
    int layer = 0;
    bool vertical = false;
    int32_t c = 0;
    int32_t a0 = 0;
    int32_t a1 = 0;
    std::vector<Section> sections;
};

struct Drill {
    IPt at;
    int layer0 = 0;
    int layer1 = 0;
    int room0 = -1;
    int room1 = -1;
    bool occupied = false;
    int back_door = -1;
    int back_sec = -1;
    int back_drill = -1;
};

struct Page {
    IBox box;
    std::vector<int> drills;
    bool occupied = false;
    int back_door = -1;
    int back_sec = -1;
};

struct Maze {
    std::vector<Room> rooms;
    std::vector<Door> doors;
    std::vector<Drill> drills;
    std::vector<Page> pages;
    std::vector<std::vector<int>> drills_at;
    // rooms covered by several rippable items carry rip_item = -3 - index into rip_sets
    std::vector<std::vector<int>> rip_sets;
    int built_gen = -1;
    int built_half_w = -1;
    bool built_rip = false;
    int built_net = -1;
    std::pair<const int*, int> rip_span(const int& id) const
    {
        if (id >= 0)
            return {&id, 1};
        if (id <= -3) {
            const std::vector<int>& set = rip_sets[static_cast<std::size_t>(-3 - id)];
            return {set.data(), static_cast<int>(set.size())};
        }
        return {nullptr, 0};
    }
    void reset()
    {
        rooms.clear();
        doors.clear();
        drills.clear();
        pages.clear();
        drills_at.clear();
        rip_sets.clear();
        built_gen = -1;
        built_half_w = -1;
        built_rip = false;
        built_net = -1;
    }
    void clear_wave()
    {
        for (Room& room : rooms) {
            room.start = false;
            room.dest = false;
            room.has_goal = false;
            room.goal_d = std::numeric_limits<int64_t>::max();
            room.has_start = false;
            room.start_d = std::numeric_limits<int64_t>::max();
        }
        for (Door& door : doors) {
            for (Section& sec : door.sections) {
                sec.occupied = false;
                sec.back_door = -1;
                sec.back_sec = -1;
                sec.ripped = false;
                sec.rip_item = -1;
                sec.at = sec.mid;
            }
        }
        for (Drill& drill : drills) {
            drill.occupied = false;
            drill.back_door = -1;
            drill.back_sec = -1;
        }
    }
};

struct Step {
    enum Type { Door, Drill } type = Door;
    int door = -1;
    int sec = -1;
    int drill = -1;
};

struct Found {
    bool ok = false;
    std::vector<IPt> pts;
    std::vector<int> pt_layer;
    int layer = 0;
    std::vector<int> rip_items;
    int via_x = 0;
    int via_y = 0;
    bool has_via = false;
    int via_layer0 = 0;
    int via_layer1 = 0;
    bool has_goal = false;
    IPt goal{};
    IPt goal_entry{};
    int goal_layer = 0;
    bool has_start = false;
    IPt start_at{};
    IPt start_entry{};
};

std::atomic<int> g_air_valid{0};
std::atomic<int32_t> g_air_x0{0};
std::atomic<int32_t> g_air_y0{0};
std::atomic<int32_t> g_air_x1{0};
std::atomic<int32_t> g_air_y1{0};

void set_airline(bool on, int32_t x0, int32_t y0, int32_t x1, int32_t y1)
{
    g_air_x0.store(x0, std::memory_order_relaxed);
    g_air_y0.store(y0, std::memory_order_relaxed);
    g_air_x1.store(x1, std::memory_order_relaxed);
    g_air_y1.store(y1, std::memory_order_relaxed);
    g_air_valid.store(on ? 1 : 0, std::memory_order_release);
}

struct PaintClock {
    interactive::BoardHandling* hdlg = nullptr;
    std::chrono::steady_clock::time_point next{};
    void tick(bool force = false)
    {
        if (hdlg == nullptr || hdlg->get_panel() == nullptr)
            return;
        std::chrono::steady_clock::time_point now = std::chrono::steady_clock::now();
        if (!force && now < next)
            return;
        next = now + std::chrono::seconds(1);
        hdlg->repaint();
    }
};

PaintClock* g_paint = nullptr;

void note_paint()
{
    if (g_paint != nullptr)
        g_paint->tick(false);
}

void note_paint_now()
{
    if (g_paint != nullptr)
        g_paint->tick(true);
}

struct PaintScope {
    PaintClock clock;
    explicit PaintScope(interactive::BoardHandling* hdlg)
    {
        clock.hdlg = hdlg;
        clock.tick(true);
        g_paint = &clock;
    }
    ~PaintScope()
    {
        g_paint = nullptr;
    }
};


void refresh_angle(Snap& s)
{
    s.angle = 0;
    if (s.board == nullptr || s.board->rules == nullptr)
        return;
    board::AngleRestriction* restr = s.board->rules->get_trace_angle_restriction();
    if (restr == nullptr)
        return;
    if (restr->no == 0)
        s.angle = 2;
    else if (restr->no == 1)
        s.angle = 1;
}

int32_t pt_coord(geometry::planar::Point* p, bool x)
{
    if (p == nullptr)
        return 0;
    if (auto* ip = dynamic_cast<geometry::planar::IntPoint*>(p))
        return x ? ip->x : ip->y;
    geometry::planar::FloatPoint* f = p->to_float();
    if (f == nullptr)
        return 0;
    int32_t v = static_cast<int32_t>(std::lround(x ? f->x : f->y));
    delete f;
    return v;
}

int32_t pt_x(geometry::planar::Point* p)
{
    return pt_coord(p, true);
}

int32_t pt_y(geometry::planar::Point* p)
{
    return pt_coord(p, false);
}

IBox from_box(geometry::planar::IntBox* b)
{
    IBox o;
    if (b == nullptr || b->ll == nullptr || b->ur == nullptr)
        return o;
    o.x0 = b->ll->x;
    o.y0 = b->ll->y;
    o.x1 = b->ur->x;
    o.y1 = b->ur->y;
    if (o.x0 > o.x1)
        std::swap(o.x0, o.x1);
    if (o.y0 > o.y1)
        std::swap(o.y0, o.y1);
    return o;
}

// Item::bounding_box() returns a fresh, a cached or the item's own box depending on the type.
IBox item_box(board::Item* item)
{
    if (auto* trace = dynamic_cast<board::PolylineTrace*>(item)) {
        IBox o = from_box(trace->polyline()->bounding_box());
        const int32_t w = trace->get_half_width();
        return IBox{o.x0 - w, o.y0 - w, o.x1 + w, o.y1 + w};
    }
    if (auto* drill = dynamic_cast<board::DrillItem*>(item)) {
        IBox o;
        bool any = false;
        bool circles = true;
        for (int32_t i = 0; circles && i < drill->tile_shape_count(); ++i) {
            geometry::planar::Shape* shape = drill->get_shape(i);
            if (shape == nullptr)
                continue;
            auto* circle = java::narrow<geometry::planar::Circle*>(shape);
            if (circle == nullptr) {
                circles = false;
                break;
            }
            IBox c{circle->center->x - circle->radius, circle->center->y - circle->radius,
                circle->center->x + circle->radius, circle->center->y + circle->radius};
            o = any ? IBox{std::min(o.x0, c.x0), std::min(o.y0, c.y0), std::max(o.x1, c.x1), std::max(o.y1, c.y1)} : c;
            any = true;
        }
        if (circles && any)
            return o;
    }
    return from_box(item->bounding_box());
}

bool overlap(const IBox& a, const IBox& b)
{
    return a.x0 < b.x1 && b.x0 < a.x1 && a.y0 < b.y1 && b.y0 < a.y1;
}

bool contains_pt(const IBox& b, int32_t x, int32_t y)
{
    return x >= b.x0 && x <= b.x1 && y >= b.y0 && y <= b.y1;
}

bool on_ring_border(const std::vector<IPt>& ring, int32_t x, int32_t y)
{
    const std::size_t n = ring.size();
    if (n < 2)
        return false;
    for (std::size_t i = 0, j = n - 1; i < n; j = i++) {
        const IPt& a = ring[j];
        const IPt& b = ring[i];
        int64_t cross = static_cast<int64_t>(b.x - a.x) * (y - a.y) - static_cast<int64_t>(b.y - a.y) * (x - a.x);
        if (cross != 0)
            continue;
        if (x < std::min(a.x, b.x) || x > std::max(a.x, b.x))
            continue;
        if (y < std::min(a.y, b.y) || y > std::max(a.y, b.y))
            continue;
        return true;
    }
    return false;
}

bool in_ring(const std::vector<IPt>& ring, int32_t x, int32_t y)
{
    if (on_ring_border(ring, x, y))
        return true;
    bool inside = false;
    const std::size_t n = ring.size();
    if (n < 3)
        return false;
    for (std::size_t i = 0, j = n - 1; i < n; j = i++) {
        int32_t yi = ring[i].y;
        int32_t yj = ring[j].y;
        if ((yi > y) == (yj > y))
            continue;
        double xcross = static_cast<double>(ring[j].x)
            + static_cast<double>(ring[i].x - ring[j].x) * (static_cast<double>(y - yj) / static_cast<double>(yi - yj));
        if (static_cast<double>(x) < xcross)
            inside = !inside;
    }
    return inside;
}

bool inside_board(const Snap& s, int32_t x, int32_t y)
{
    if (x < s.bx0 || x > s.bx1 || y < s.by0 || y > s.by1)
        return false;
    if (!s.has_outline)
        return true;
    for (const std::vector<IPt>& ring : s.outline) {
        if (in_ring(ring, x, y))
            return true;
    }
    return false;
}

// inside_board for many x on one row, with the arithmetic of on_ring_border and in_ring
struct BoardRow {
    const Snap& s;
    bool in_y = false;
    std::vector<std::pair<int32_t, int32_t>> border;
    std::vector<std::vector<double>> cross;

    BoardRow(const Snap& snap, int32_t y) : s(snap)
    {
        in_y = y >= s.by0 && y <= s.by1;
        if (!in_y || !s.has_outline)
            return;
        for (const std::vector<IPt>& ring : s.outline) {
            const std::size_t n = ring.size();
            std::vector<double> xs;
            if (n >= 2) {
                for (std::size_t i = 0, j = n - 1; i < n; j = i++) {
                    const IPt& a = ring[j];
                    const IPt& b = ring[i];
                    if (y < std::min(a.y, b.y) || y > std::max(a.y, b.y))
                        continue;
                    int64_t dy = b.y - a.y;
                    if (dy == 0) {
                        border.emplace_back(std::min(a.x, b.x), std::max(a.x, b.x));
                        continue;
                    }
                    int64_t num = static_cast<int64_t>(b.x - a.x) * (y - a.y);
                    if (num % dy == 0) {
                        int64_t x = a.x + num / dy;
                        if (x >= std::min(a.x, b.x) && x <= std::max(a.x, b.x))
                            border.emplace_back(static_cast<int32_t>(x), static_cast<int32_t>(x));
                    }
                }
            }
            if (n >= 3) {
                for (std::size_t i = 0, j = n - 1; i < n; j = i++) {
                    int32_t yi = ring[i].y;
                    int32_t yj = ring[j].y;
                    if ((yi > y) == (yj > y))
                        continue;
                    xs.push_back(static_cast<double>(ring[j].x)
                        + static_cast<double>(ring[i].x - ring[j].x) * (static_cast<double>(y - yj) / static_cast<double>(yi - yj)));
                }
                std::sort(xs.begin(), xs.end());
            }
            cross.push_back(std::move(xs));
        }
        std::sort(border.begin(), border.end());
        pos.assign(cross.size(), 0);
        if (!in_y)
            return;
        steps.push_back(s.bx0);
        steps.push_back(static_cast<int64_t>(s.bx1) + 1);
        for (const auto& b : border) {
            steps.push_back(b.first);
            steps.push_back(static_cast<int64_t>(b.second) + 1);
        }
        for (const std::vector<double>& xs : cross)
            for (double v : xs)
                steps.push_back(static_cast<int64_t>(std::ceil(v)));
        std::sort(steps.begin(), steps.end());
    }

    // smallest value above x where inside() may change; x must not decrease between calls
    int64_t next_step(int32_t x)
    {
        while (step_pos < steps.size() && steps[step_pos] <= x)
            ++step_pos;
        return step_pos < steps.size() ? steps[step_pos] : std::numeric_limits<int64_t>::max();
    }

    // x must not decrease between calls
    bool inside(int32_t x)
    {
        if (!in_y || x < s.bx0 || x > s.bx1)
            return false;
        if (!s.has_outline)
            return true;
        for (; border_pos < border.size() && border[border_pos].first <= x; ++border_pos)
            border_max = std::max(border_max, static_cast<int64_t>(border[border_pos].second));
        if (border_max >= x)
            return true;
        for (std::size_t r = 0; r < cross.size(); ++r) {
            const std::vector<double>& xs = cross[r];
            std::size_t& p = pos[r];
            while (p < xs.size() && xs[p] <= static_cast<double>(x))
                ++p;
            if ((xs.size() - p) % 2 != 0)
                return true;
        }
        return false;
    }

private:
    std::vector<std::size_t> pos;
    std::vector<int64_t> steps;
    std::size_t step_pos = 0;
    std::size_t border_pos = 0;
    int64_t border_max = std::numeric_limits<int64_t>::min();
};

bool near_edge(const Snap& s, IPt a, IPt b, int gap);
bool path_clear(const Snap& s, int layer, int net, int margin, const std::vector<IPt>& path, const std::vector<int>& ignore);

bool via_fits(const Snap& s, int32_t x, int32_t y)
{
    int r = std::max(0, s.via_r);
    if (!inside_board(s, x, y) || !inside_board(s, x - r, y) || !inside_board(s, x + r, y)
        || !inside_board(s, x, y - r) || !inside_board(s, x, y + r))
        return false;
    int oct_r = static_cast<int>(std::ceil(r * 1.0824)) + 2;
    return !near_edge(s, IPt{x, y}, IPt{x, y}, oct_r + s.edge_cl);
}

bool touches_pt(const IBox& b, int32_t x, int32_t y, int32_t pad)
{
    return x >= b.x0 - pad && x <= b.x1 + pad && y >= b.y0 - pad && y <= b.y1 + pad;
}

double dist2_seg(IPt a, IPt b, int32_t x, int32_t y)
{
    double dx = static_cast<double>(b.x - a.x);
    double dy = static_cast<double>(b.y - a.y);
    double len2 = dx * dx + dy * dy;
    double t = 0;
    if (len2 > 0)
        t = ((static_cast<double>(x - a.x) * dx) + (static_cast<double>(y - a.y) * dy)) / len2;
    if (t < 0)
        t = 0;
    if (t > 1)
        t = 1;
    double px = static_cast<double>(a.x) + t * dx - x;
    double py = static_cast<double>(a.y) + t * dy - y;
    return px * px + py * py;
}

bool near_edge(const Snap& s, IPt a, IPt b, int gap)
{
    if (gap <= 0)
        return false;
    if (!s.has_outline)
        return std::min(a.x, b.x) - s.bx0 < gap || s.bx1 - std::max(a.x, b.x) < gap
            || std::min(a.y, b.y) - s.by0 < gap || s.by1 - std::max(a.y, b.y) < gap;
    const double lim = static_cast<double>(gap) * static_cast<double>(gap);
    for (const std::vector<IPt>& ring : s.outline) {
        for (std::size_t i = 0, j = ring.size() - 1; i < ring.size(); j = i++) {
            const IPt& c = ring[j];
            const IPt& d = ring[i];
            if (dist2_seg(c, d, a.x, a.y) < lim || dist2_seg(c, d, b.x, b.y) < lim)
                return true;
            if (dist2_seg(a, b, c.x, c.y) < lim || dist2_seg(a, b, d.x, d.y) < lim)
                return true;
        }
    }
    return false;
}

IBox inflate(IBox b, int32_t m)
{
    b.x0 -= m;
    b.y0 -= m;
    b.x1 += m;
    b.y1 += m;
    return b;
}

void set_trace_corners(SnapItem& it, std::vector<IPt> corners, int half_w)
{
    it.corners = std::move(corners);
    if (it.corners.empty())
        return;
    IBox b{it.corners.front().x, it.corners.front().y, it.corners.front().x, it.corners.front().y};
    for (const IPt& p : it.corners) {
        b.x0 = std::min(b.x0, p.x);
        b.y0 = std::min(b.y0, p.y);
        b.x1 = std::max(b.x1, p.x);
        b.y1 = std::max(b.y1, p.y);
    }
    it.box = inflate(b, half_w);
    it.center = it.corners.front();
}

int clamp_layer(int layer, int layers)
{
    if (layer < 0)
        return 0;
    if (layer >= layers)
        return layers - 1;
    return layer;
}

void add_coord(std::vector<int32_t>& v, int32_t c, int32_t lo, int32_t hi)
{
    if (c < lo)
        c = lo;
    if (c > hi)
        c = hi;
    v.push_back(c);
}

void unique_sorted(std::vector<int32_t>& v)
{
    std::sort(v.begin(), v.end());
    v.erase(std::unique(v.begin(), v.end()), v.end());
}

void cluster_coords(std::vector<int32_t>& v, int32_t min_gap, std::size_t cap)
{
    unique_sorted(v);
    if (v.size() <= cap)
        return;
    const int n = static_cast<int>(v.size());
    std::vector<int> prev(static_cast<std::size_t>(n));
    std::vector<int> next(static_cast<std::size_t>(n));
    std::vector<char> dead(static_cast<std::size_t>(n), 0);
    for (int i = 0; i < n; ++i) {
        prev[static_cast<std::size_t>(i)] = i - 1;
        next[static_cast<std::size_t>(i)] = i + 1 == n ? -1 : i + 1;
    }
    using Gap = std::pair<int32_t, int>;
    std::priority_queue<Gap, std::vector<Gap>, std::greater<Gap>> heap;
    for (int i = 1; i < n; ++i)
        heap.push(Gap{static_cast<int32_t>(v[static_cast<std::size_t>(i)] - v[static_cast<std::size_t>(i - 1)]), i});
    int alive = n;
    while (alive > static_cast<int>(cap) && alive > 1 && !heap.empty()) {
        Gap top = heap.top();
        if (min_gap > 0 && top.first > min_gap)
            break;
        if (min_gap >= 100 && top.first == min_gap)
            break;
        heap.pop();
        int i = top.second;
        if (i <= 0 || dead[static_cast<std::size_t>(i)])
            continue;
        int left = prev[static_cast<std::size_t>(i)];
        if (left < 0 || static_cast<int32_t>(v[static_cast<std::size_t>(i)] - v[static_cast<std::size_t>(left)]) != top.first)
            continue;
        int right = next[static_cast<std::size_t>(i)];
        dead[static_cast<std::size_t>(i)] = 1;
        next[static_cast<std::size_t>(left)] = right;
        if (right >= 0)
            prev[static_cast<std::size_t>(right)] = left;
        --alive;
        if (right >= 0)
            heap.push(Gap{static_cast<int32_t>(v[static_cast<std::size_t>(right)] - v[static_cast<std::size_t>(left)]), right});
    }
    std::vector<int32_t> kept;
    kept.reserve(static_cast<std::size_t>(std::max(alive, 0)));
    for (int i = 0; i >= 0; i = next[static_cast<std::size_t>(i)])
        kept.push_back(v[static_cast<std::size_t>(i)]);
    v.swap(kept);
}

void read_snapshot(Snap& s, board::RoutingBoard* board, interactive::Settings* settings, int via_costs, int pass_no, bool fanout, bool bump = true)
{
    std::unordered_map<board::Item*, SnapItem> kept;
    if (s.board == board) {
        kept.reserve(s.items.size() * 2 + 1);
        for (SnapItem& row : s.items) {
            if (row.item != nullptr)
                kept.emplace(row.item, std::move(row));
        }
    }
    s.items.clear();
    s.outline.clear();
    s.has_outline = false;
    s.edge_cl = 0;
    s.cost_h.clear();
    s.cost_v.clear();
    s.board = board;
    s.layers = std::max(1, static_cast<int>(board->get_layer_count()));
    s.layer_on.assign(static_cast<std::size_t>(s.layers), 1);
    if (settings != nullptr) {
        for (int i = 0; i < s.layers; ++i)
            s.layer_on[static_cast<std::size_t>(i)] = settings->autoroute_settings->get_layer_active(i) ? 1 : 0;
    }
    s.fanout = fanout;
    s.forbid_rip.clear();
    s.vias_allowed = settings == nullptr || settings->autoroute_settings->get_vias_allowed();
    int start_ripup = 100;
    if (settings != nullptr)
        start_ripup = std::max(1, static_cast<int>(settings->autoroute_settings->get_start_ripup_costs()));
    if (s.ripup_start > 0)
        start_ripup = s.ripup_start;
    s.ripup_cost = start_ripup * std::max(1, pass_no);
    s.ripup = true;
    refresh_angle(s);
    IBox bounds = from_box(board->bounding_box);
    s.bx0 = bounds.x0;
    s.by0 = bounds.y0;
    s.bx1 = bounds.x1;
    s.by1 = bounds.y1;
    s.half_w = std::max(1, static_cast<int>(board->rules->get_default_trace_half_width(0)));
    s.clearance = std::max(0, static_cast<int>(board->rules->clearance_matrix->max_value(0)));
    s.cost_h.assign(static_cast<std::size_t>(s.layers), 1.0);
    s.cost_v.assign(static_cast<std::size_t>(s.layers), 1.0);
    if (settings != nullptr) {
        interactive::AutorouteSettings* ar = settings->autoroute_settings;
        for (int i = 0; i < s.layers && i < ar->preferred_direction_trace_cost_arr.length; ++i) {
            s.cost_h[static_cast<std::size_t>(i)] = std::max(0.01, ar->get_horizontal_trace_costs(i));
            s.cost_v[static_cast<std::size_t>(i)] = std::max(0.01, ar->get_vertical_trace_costs(i));
            if (s.flat_dir) {
                double low = std::min(s.cost_h[static_cast<std::size_t>(i)], s.cost_v[static_cast<std::size_t>(i)]);
                s.cost_h[static_cast<std::size_t>(i)] = low;
                s.cost_v[static_cast<std::size_t>(i)] = low;
            }
        }
    }
    rules::ViaRule* rule = board->rules->get_default_via_rule();
    if (rule != nullptr && rule->via_count() > 0 && rule->get_via(0) != nullptr) {
        s.via_pad = rule->get_via(0)->get_padstack();
        s.via_clearance = rule->get_via(0)->clearance_class;
        if (s.via_pad != nullptr) {
            geometry::planar::ConvexShape* shape = s.via_pad->get_shape(s.via_pad->from_layer());
            if (auto* circle = java::narrow<geometry::planar::Circle*>(shape)) {
                s.via_r = std::max(1, static_cast<int>(circle->radius));
            } else if (shape != nullptr && shape->bounding_box() != nullptr) {
                IBox vb = from_box(shape->bounding_box());
                s.via_r = std::max(1, std::max(vb.x1 - vb.x0, vb.y1 - vb.y0) / 2);
            }
        }
    }
    if (s.via_pad == nullptr)
        s.vias_allowed = false;
    s.via_cost = (via_costs > 0 ? via_costs : 50) * std::max(1, s.via_r);

    java::util::Iterator<datastructures::UndoableObjects_UndoableObjectNode*>* it = board->item_list->start_read_object();
    std::unique_ptr<java::util::Iterator<datastructures::UndoableObjects_UndoableObjectNode*>> it_owner(it);
    for (;;) {
        datastructures::UndoableObjects_Storable* ob = board->item_list->read_object(it);
        if (java::fr_eq(ob, nullptr))
            break;
        board::Item* item = dynamic_cast<board::Item*>(ob);
        if (item == nullptr)
            continue;
        if (auto* outline = dynamic_cast<board::BoardOutline*>(item)) {
            for (int l = 0; l < s.layers; ++l)
                s.edge_cl = std::max(s.edge_cl, static_cast<int>(board->rules->clearance_matrix->max_value(outline->clearance_class_no(), l)) + outline->get_half_width());
            for (int32_t si = 0; si < outline->shape_count(); ++si) {
                geometry::planar::PolylineShape* shape = outline->get_shape(si);
                if (shape == nullptr)
                    continue;
                int32_t n = shape->border_line_count();
                std::vector<IPt> ring;
                ring.reserve(static_cast<std::size_t>(std::max(0, n)));
                for (int32_t k = 0; k < n; ++k) {
                    geometry::planar::Point* corner = shape->corner(k);
                    if (corner == nullptr)
                        continue;
                    ring.push_back(IPt{pt_x(corner), pt_y(corner)});
                }
                if (ring.size() >= 3)
                    s.outline.push_back(std::move(ring));
            }
            continue;
        }
        auto kept_item = kept.find(item);
        if (kept_item != kept.end()) {
            // shoving moves drill items in place, so a kept row must still match the item
            bool same = kept_item->second.fixed == item->is_user_fixed();
            if (auto* drill = dynamic_cast<board::DrillItem*>(item)) {
                geometry::planar::Point* center = drill->get_center();
                same = same && center != nullptr && pt_x(center) == kept_item->second.center.x && pt_y(center) == kept_item->second.center.y;
            }
            if (same) {
                s.items.push_back(std::move(kept_item->second));
                kept.erase(kept_item);
                continue;
            }
            kept.erase(kept_item);
        }
        SnapItem row;
        row.item = item;
        row.net = item->net_count() > 0 ? item->get_net_no(0) : 0;
        row.layer0 = clamp_layer(item->first_layer(), s.layers);
        row.layer1 = clamp_layer(item->last_layer(), s.layers);
        if (row.layer0 > row.layer1)
            std::swap(row.layer0, row.layer1);
        row.clearance = item->clearance_class_no();
        row.fixed = item->is_user_fixed();
        row.box = item_box(item);
        row.center.x = (row.box.x0 + row.box.x1) / 2;
        row.center.y = (row.box.y0 + row.box.y1) / 2;
        if (dynamic_cast<board::ConductionArea*>(item) != nullptr)
            row.kind = Kind::Plane;
        else if (dynamic_cast<board::Pin*>(item) != nullptr)
            row.kind = Kind::Pin;
        else if (dynamic_cast<board::Via*>(item) != nullptr)
            row.kind = Kind::Via;
        else if (dynamic_cast<board::PolylineTrace*>(item) != nullptr) {
            row.kind = Kind::Trace;
            geometry::planar::Polyline* poly = static_cast<board::PolylineTrace*>(item)->polyline();
            if (poly != nullptr) {
                for (int32_t c = 0; c < poly->corner_count(); ++c) {
                    geometry::planar::Point* corner = poly->corner(c);
                    row.corners.push_back(IPt{pt_x(corner), pt_y(corner)});
                }
                if (!row.corners.empty())
                    row.center = row.corners.front();
            }
        } else if (dynamic_cast<board::ComponentObstacleArea*>(item) != nullptr
            || dynamic_cast<board::ComponentOutline*>(item) != nullptr) {
            continue;
        } else if (dynamic_cast<board::ViaObstacleArea*>(item) != nullptr) {
            row.kind = Kind::ViaKeepout;
        } else if (dynamic_cast<board::ObstacleArea*>(item) != nullptr) {
            row.kind = Kind::Keepout;
            row.hard = true;
        } else
            continue;
        if (row.kind == Kind::Pin || row.kind == Kind::Via) {
            geometry::planar::Point* center = nullptr;
            if (auto* drill = dynamic_cast<board::DrillItem*>(item))
                center = drill->get_center();
            if (center != nullptr) {
                row.center.x = pt_x(center);
                row.center.y = pt_y(center);
            }
        }
        s.items.push_back(std::move(row));
    }
    if (!s.outline.empty()) {
        int32_t x0 = std::numeric_limits<int32_t>::max();
        int32_t y0 = x0;
        int32_t x1 = std::numeric_limits<int32_t>::min();
        int32_t y1 = x1;
        for (const std::vector<IPt>& ring : s.outline) {
            for (const IPt& p : ring) {
                x0 = std::min(x0, p.x);
                y0 = std::min(y0, p.y);
                x1 = std::max(x1, p.x);
                y1 = std::max(y1, p.y);
            }
        }
        if (x0 < x1 && y0 < y1) {
            s.bx0 = x0;
            s.by0 = y0;
            s.bx1 = x1;
            s.by1 = y1;
            s.has_outline = true;
        }
    }

    std::vector<int> parent(s.items.size());
    for (std::size_t i = 0; i < parent.size(); ++i)
        parent[i] = static_cast<int>(i);
    auto find = [&](auto&& self, int x) -> int {
        if (parent[static_cast<std::size_t>(x)] != x)
            parent[static_cast<std::size_t>(x)] = self(self, parent[static_cast<std::size_t>(x)]);
        return parent[static_cast<std::size_t>(x)];
    };
    auto unite = [&](int a, int b) {
        a = find(find, a);
        b = find(find, b);
        if (a != b)
            parent[static_cast<std::size_t>(a)] = b;
    };
    struct TouchKey {
        int net = 0;
        int32_t x = 0;
        int32_t y = 0;
        bool operator==(const TouchKey& o) const
        {
            return net == o.net && x == o.x && y == o.y;
        }
    };
    struct TouchHash {
        std::size_t operator()(const TouchKey& k) const
        {
            std::size_t h = static_cast<std::size_t>(k.net) * 1315423911u;
            h ^= static_cast<std::size_t>(static_cast<uint32_t>(k.x)) * 2654435761u;
            h ^= static_cast<std::size_t>(static_cast<uint32_t>(k.y)) * 97531u;
            return h;
        }
    };
    std::unordered_map<TouchKey, std::vector<int>, TouchHash> at;
    auto touch = [&](int index, int32_t x, int32_t y) {
        int net = s.items[static_cast<std::size_t>(index)].net;
        if (net <= 0)
            return;
        TouchKey key{net, x, y};
        std::vector<int>& bucket = at[key];
        const SnapItem& mine = s.items[static_cast<std::size_t>(index)];
        for (int other : bucket) {
            const SnapItem& there = s.items[static_cast<std::size_t>(other)];
            if (mine.layer0 <= there.layer1 && there.layer0 <= mine.layer1)
                unite(index, other);
        }
        bucket.push_back(index);
    };
    for (std::size_t i = 0; i < s.items.size(); ++i) {
        const SnapItem& it = s.items[i];
        if (it.net <= 0)
            continue;
        if (it.kind == Kind::Pin || it.kind == Kind::Via)
            touch(static_cast<int>(i), it.center.x, it.center.y);
        else if (it.kind == Kind::Trace && !it.corners.empty()) {
            touch(static_cast<int>(i), it.corners.front().x, it.corners.front().y);
            if (it.corners.size() > 1)
                touch(static_cast<int>(i), it.corners.back().x, it.corners.back().y);
        }
    }
    for (std::size_t i = 0; i < s.items.size(); ++i) {
        if (s.items[i].kind != Kind::Plane)
            continue;
        for (std::size_t k = 0; k < s.items.size(); ++k) {
            if (s.items[k].net != s.items[i].net)
                continue;
            if (contains_pt(s.items[i].box, s.items[k].center.x, s.items[k].center.y))
                unite(static_cast<int>(i), static_cast<int>(k));
        }
    }
    int next_comp = 0;
    std::unordered_map<int, int> comp_of;
    for (std::size_t i = 0; i < s.items.size(); ++i) {
        if (s.items[i].kind != Kind::Pin && s.items[i].kind != Kind::Via && s.items[i].kind != Kind::Trace && s.items[i].kind != Kind::Plane)
            continue;
        if (s.items[i].net <= 0)
            continue;
        int root = find(find, static_cast<int>(i));
        auto known = comp_of.find(root);
        if (known == comp_of.end())
            known = comp_of.emplace(root, next_comp++).first;
        s.items[i].component = known->second;
    }
    ++s.version;
    if (bump)
        ++s.generation;
}

int item_half_width(const Snap& s, int net, int layer)
{
    if (net > 0)
        return std::max(1, static_cast<int>(s.board->rules->get_trace_half_width(net, layer)));
    return s.half_w;
}

int trace_half(const Snap& s, const SnapItem& it)
{
    if (auto* trace = dynamic_cast<board::Trace*>(it.item))
        return std::max(1, static_cast<int>(trace->get_half_width()));
    return item_half_width(s, it.net, it.layer0);
}

int pair_clearance(const Snap& s, int class_a, int class_b, int layer)
{
    return std::max(0, static_cast<int>(s.board->rules->clearance_matrix->value(class_a, class_b, layer)));
}

bool on_layer(const SnapItem& it, int layer)
{
    return layer >= it.layer0 && layer <= it.layer1;
}

struct Block {
    IBox box;
    int rip_item = -1;
    bool hard = false;
    bool keepout = false;
    bool pin = false;
};

bool segment_hits(const Snap& s, int layer, IPt a, IPt b, int net, int margin, const std::vector<int>& ignore)
{
    auto ignored = [&](int idx) {
        return std::find(ignore.begin(), ignore.end(), idx) != ignore.end();
    };
    struct HitGrid {
        const Snap* snap = nullptr;
        std::size_t n = 0;
        int layer = -1;
        int net = -1;
        int margin = -1;
        int generation = -1;
        int gcols = 48;
        int grows = 48;
        std::vector<std::vector<int>> buckets;
        std::vector<int> big;
        std::vector<int> grow;
    };
    static HitGrid grid;
    if (grid.snap != &s || grid.n != s.items.size() || grid.layer != layer || grid.net != net || grid.margin != margin || grid.generation != s.version) {
        grid.snap = &s;
        grid.n = s.items.size();
        grid.layer = layer;
        grid.net = net;
        grid.margin = margin;
        grid.generation = s.version;
        grid.buckets.assign(static_cast<std::size_t>(grid.gcols * grid.grows), {});
        grid.big.clear();
        grid.grow.assign(s.items.size(), 0);
        const int64_t span_x = std::max<int64_t>(1, static_cast<int64_t>(s.bx1) - s.bx0);
        const int64_t span_y = std::max<int64_t>(1, static_cast<int64_t>(s.by1) - s.by0);
        auto col_of = [&](int32_t x) {
            int col = static_cast<int>(((static_cast<int64_t>(x) - s.bx0) * grid.gcols) / span_x);
            return std::min(grid.gcols - 1, std::max(0, col));
        };
        auto row_of = [&](int32_t y) {
            int row = static_cast<int>(((static_cast<int64_t>(y) - s.by0) * grid.grows) / span_y);
            return std::min(grid.grows - 1, std::max(0, row));
        };
        for (std::size_t k = 0; k < s.items.size(); ++k) {
            const SnapItem& it = s.items[k];
            if (!on_layer(it, layer) || it.kind == Kind::Plane)
                continue;
            if (it.net == net && it.net > 0 && it.kind != Kind::Keepout)
                continue;
            if (it.kind != Kind::Keepout && !it.hard && !it.fixed && it.kind != Kind::Pin && it.kind != Kind::Via && it.kind != Kind::Trace)
                continue;
            int pad = margin + pair_clearance(s, 1, it.clearance, layer);
            grid.grow[k] = pad;
            int c0 = col_of(it.box.x0 - pad);
            int c1 = col_of(it.box.x1 + pad);
            int r0 = row_of(it.box.y0 - pad);
            int r1 = row_of(it.box.y1 + pad);
            if ((c1 - c0 + 1) * (r1 - r0 + 1) > 24) {
                grid.big.push_back(static_cast<int>(k));
                continue;
            }
            for (int r = r0; r <= r1; ++r)
                for (int c = c0; c <= c1; ++c)
                    grid.buckets[static_cast<std::size_t>(r * grid.gcols + c)].push_back(static_cast<int>(k));
        }
        grid.snap = &s;
    }
    const int64_t span_x = std::max<int64_t>(1, static_cast<int64_t>(s.bx1) - s.bx0);
    const int64_t span_y = std::max<int64_t>(1, static_cast<int64_t>(s.by1) - s.by0);
    auto col_of = [&](int32_t x) {
        int col = static_cast<int>(((static_cast<int64_t>(x) - s.bx0) * grid.gcols) / span_x);
        return std::min(grid.gcols - 1, std::max(0, col));
    };
    auto row_of = [&](int32_t y) {
        int row = static_cast<int>(((static_cast<int64_t>(y) - s.by0) * grid.grows) / span_y);
        return std::min(grid.grows - 1, std::max(0, row));
    };
    auto seg_cross = [](IPt p, IPt q, IPt c, IPt d) {
        auto orient = [](IPt u, IPt v, IPt w) {
            int64_t val = static_cast<int64_t>(v.x - u.x) * (w.y - u.y) - static_cast<int64_t>(v.y - u.y) * (w.x - u.x);
            return (val > 0) - (val < 0);
        };
        int o1 = orient(p, q, c);
        int o2 = orient(p, q, d);
        int o3 = orient(c, d, p);
        int o4 = orient(c, d, q);
        if (o1 != o2 && o3 != o4)
            return true;
        auto on_seg = [](IPt u, IPt v, IPt w) {
            return std::min(u.x, v.x) <= w.x && w.x <= std::max(u.x, v.x) && std::min(u.y, v.y) <= w.y && w.y <= std::max(u.y, v.y);
        };
        if (o1 == 0 && on_seg(p, q, c))
            return true;
        if (o2 == 0 && on_seg(p, q, d))
            return true;
        if (o3 == 0 && on_seg(c, d, p))
            return true;
        if (o4 == 0 && on_seg(c, d, q))
            return true;
        return false;
    };
    auto seg_hits_box = [&](IBox box) {
        auto inside = [&](IPt p) {
            return p.x >= box.x0 && p.x <= box.x1 && p.y >= box.y0 && p.y <= box.y1;
        };
        if (inside(a) || inside(b))
            return true;
        return seg_cross(a, b, IPt{box.x0, box.y0}, IPt{box.x1, box.y0})
            || seg_cross(a, b, IPt{box.x1, box.y0}, IPt{box.x1, box.y1})
            || seg_cross(a, b, IPt{box.x1, box.y1}, IPt{box.x0, box.y1})
            || seg_cross(a, b, IPt{box.x0, box.y1}, IPt{box.x0, box.y0});
    };
    auto segs_near = [&](IPt c, IPt d, double lim) {
        if (dist2_seg(c, d, a.x, a.y) < lim || dist2_seg(c, d, b.x, b.y) < lim)
            return true;
        if (dist2_seg(a, b, c.x, c.y) < lim || dist2_seg(a, b, d.x, d.y) < lim)
            return true;
        return lim > 0 && seg_cross(a, b, c, d);
    };
    auto hit = [&](int index) {
        if (ignored(index))
            return false;
        const SnapItem& it = s.items[static_cast<std::size_t>(index)];
        if (it.kind == Kind::Trace && it.corners.size() >= 2) {
            int need = grid.grow[static_cast<std::size_t>(index)] + item_half_width(s, it.net, layer);
            int32_t qx0 = std::min(a.x, b.x) - need;
            int32_t qy0 = std::min(a.y, b.y) - need;
            int32_t qx1 = std::max(a.x, b.x) + need;
            int32_t qy1 = std::max(a.y, b.y) + need;
            if (it.box.x1 < qx0 || it.box.x0 > qx1 || it.box.y1 < qy0 || it.box.y0 > qy1)
                return false;
            double lim = static_cast<double>(need) * static_cast<double>(need);
            for (std::size_t k = 1; k < it.corners.size(); ++k) {
                if (segs_near(it.corners[k - 1], it.corners[k], lim))
                    return true;
            }
            return false;
        }
        int pad = grid.grow[static_cast<std::size_t>(index)];
        IBox box = inflate(it.box, pad);
        box.x0 += 1;
        box.y0 += 1;
        box.x1 -= 1;
        box.y1 -= 1;
        if (box.x1 < box.x0 || box.y1 < box.y0)
            return false;
        return seg_hits_box(box);
    };
    for (int index : grid.big) {
        if (hit(index))
            return true;
    }
    int c0 = std::min(col_of(a.x), col_of(b.x));
    int c1 = std::max(col_of(a.x), col_of(b.x));
    int r0 = std::min(row_of(a.y), row_of(b.y));
    int r1 = std::max(row_of(a.y), row_of(b.y));
    for (int r = r0; r <= r1; ++r) {
        for (int c = c0; c <= c1; ++c) {
            for (int index : grid.buckets[static_cast<std::size_t>(r * grid.gcols + c)]) {
                if (hit(index))
                    return true;
            }
        }
    }
    int steps = std::max(std::abs(a.x - b.x), std::abs(a.y - b.y));
    steps = std::max(1, steps / std::max(1, margin * 4));
    if (steps > 32)
        steps = 32;
    for (int i = 0; i <= steps; ++i) {
        int32_t x = a.x + static_cast<int32_t>((static_cast<int64_t>(b.x - a.x) * i) / steps);
        int32_t y = a.y + static_cast<int32_t>((static_cast<int64_t>(b.y - a.y) * i) / steps);
        if (!inside_board(s, x, y))
            return true;
    }
    return near_edge(s, a, b, margin + s.edge_cl + 1);
}

void mark_terminals(const Snap& s, Maze& maze, int layer, const std::vector<char>& flags, bool dest)
{
    for (std::size_t i = 0; i < s.items.size() && i < flags.size(); ++i) {
        if (!flags[i] || !on_layer(s.items[i], layer))
            continue;
        const SnapItem& it = s.items[i];
        IPt targets[2];
        int ntarget = 0;
        if (it.kind == Kind::Trace && !it.corners.empty()) {
            targets[ntarget++] = it.corners.front();
            if (it.corners.size() > 1 && (it.corners.back().x != it.corners.front().x || it.corners.back().y != it.corners.front().y))
                targets[ntarget++] = it.corners.back();
        } else
            targets[ntarget++] = it.center;
        const int margin = std::max(1, s.half_w);
        const int64_t slack = std::max(it.box.x1 - it.box.x0, it.box.y1 - it.box.y0) / 2
            + margin + pair_clearance(s, 1, it.clearance, layer);
        for (int t = 0; t < ntarget; ++t) {
            IPt c = targets[t];
            auto entry_of = [&](const Room& room) {
                return IPt{std::min(std::max(c.x, room.box.x0), room.box.x1), std::min(std::max(c.y, room.box.y0), room.box.y1)};
            };
            auto dist_of = [&](IPt e) {
                return std::abs(static_cast<int64_t>(e.x - c.x)) + std::abs(static_cast<int64_t>(e.y - c.y));
            };
            int64_t best_d = std::numeric_limits<int64_t>::max();
            for (const Room& room : maze.rooms) {
                if (room.layer == layer)
                    best_d = std::min(best_d, dist_of(entry_of(room)));
            }
            if (best_d == std::numeric_limits<int64_t>::max())
                continue;
            std::vector<std::pair<int64_t, int>> near;
            for (std::size_t r = 0; r < maze.rooms.size(); ++r) {
                if (maze.rooms[r].layer != layer)
                    continue;
                int64_t d = dist_of(entry_of(maze.rooms[r]));
                if (d <= best_d + 4 * slack)
                    near.push_back({d, static_cast<int>(r)});
            }
            std::sort(near.begin(), near.end());
            std::vector<int> none;
            auto free_to = [&](IPt e) {
                if (e.x == c.x && e.y == c.y)
                    return true;
                auto clear = [&](IPt p, IPt q) { return !segment_hits(s, layer, p, q, it.net, margin, none); };
                if (e.x == c.x || e.y == c.y || s.angle >= 2) {
                    if (clear(c, e))
                        return true;
                    if (e.x == c.x || e.y == c.y)
                        return false;
                }
                IPt e1{e.x, c.y};
                IPt e2{c.x, e.y};
                return (clear(c, e1) && clear(e1, e)) || (clear(c, e2) && clear(e2, e));
            };
            auto mark = [&](int r, int64_t d) {
                Room& room = maze.rooms[static_cast<std::size_t>(r)];
                IPt e = entry_of(room);
                if (dest) {
                    room.dest = true;
                    if (d < room.goal_d) {
                        room.goal_d = d;
                        room.goal = c;
                        room.goal_entry = e;
                        room.has_goal = true;
                    }
                } else {
                    room.start = true;
                    if (d < room.start_d) {
                        room.start_d = d;
                        room.start_at = c;
                        room.start_entry = e;
                        room.has_start = true;
                    }
                }
            };
            int64_t best_free = -1;
            int checked = 0;
            for (const auto& cand : near) {
                if (best_free >= 0 && cand.first > best_free + slack)
                    break;
                if (++checked > 48)
                    break;
                if (!free_to(entry_of(maze.rooms[static_cast<std::size_t>(cand.second)])))
                    continue;
                if (best_free < 0)
                    best_free = cand.first;
                mark(cand.second, cand.first);
            }
            if (best_free < 0 && !near.empty())
                mark(near.front().second, near.front().first);
        }
    }
}

bool build_rooms(const Snap& s, int net, int layer, int half_w, bool allow_rip, const std::vector<char>& is_start,
    const std::vector<char>& is_dest, Maze& maze, std::vector<int>& room_of_cell, bool cover_all)
{
    if (layer < 0 || layer >= static_cast<int>(s.layer_on.size()) || !s.layer_on[static_cast<std::size_t>(layer)])
        return false;
    std::vector<Block> blocks;
    for (std::size_t i = 0; i < s.items.size(); ++i) {
        const SnapItem& it = s.items[i];
        if (!on_layer(it, layer) || it.kind == Kind::Plane || it.kind == Kind::ViaKeepout)
            continue;
        if (!cover_all && i < is_start.size() && (is_start[i] || (i < is_dest.size() && is_dest[i])))
            continue;
        if (!cover_all && it.net == net && it.net > 0 && it.kind != Kind::Keepout)
            continue;
        bool soft = allow_rip && it.kind == Kind::Trace && !it.fixed && it.net > 0 && it.net != net;
        int other_half = it.kind == Kind::Trace ? item_half_width(s, it.net, layer) : 0;
        int grow = half_w + other_half + pair_clearance(s, 1, it.clearance, layer);
        auto push_box = [&](IBox box) {
            Block b;
            b.box = inflate(box, grow);
            b.hard = !soft;
            b.keepout = it.kind == Kind::Keepout;
            b.pin = it.kind == Kind::Pin || it.kind == Kind::Via;
            b.rip_item = soft ? static_cast<int>(i) : -1;
            blocks.push_back(b);
        };
        if (it.kind == Kind::Trace && it.corners.size() >= 2) {
            for (std::size_t k = 1; k < it.corners.size(); ++k) {
                const IPt& a = it.corners[k - 1];
                const IPt& c = it.corners[k];
                IBox box;
                box.x0 = std::min(a.x, c.x);
                box.x1 = std::max(a.x, c.x);
                box.y0 = std::min(a.y, c.y);
                box.y1 = std::max(a.y, c.y);
                push_box(box);
            }
        } else
            push_box(it.box);
    }
    std::vector<int32_t> xs;
    std::vector<int32_t> ys;
    xs.push_back(s.bx0);
    xs.push_back(s.bx1);
    ys.push_back(s.by0);
    ys.push_back(s.by1);
    const int32_t edge_gap = s.edge_cl > 0 ? half_w + s.edge_cl + 1 : 0;
    if (edge_gap > 0) {
        add_coord(xs, s.bx0 + edge_gap, s.bx0, s.bx1);
        add_coord(xs, s.bx1 - edge_gap, s.bx0, s.bx1);
        add_coord(ys, s.by0 + edge_gap, s.by0, s.by1);
        add_coord(ys, s.by1 - edge_gap, s.by0, s.by1);
    }
    int32_t tol = std::max(1, half_w);
    for (const Block& b : blocks) {
        add_coord(xs, b.box.x0, s.bx0, s.bx1);
        add_coord(xs, b.box.x1, s.bx0, s.bx1);
        add_coord(ys, b.box.y0, s.by0, s.by1);
        add_coord(ys, b.box.y1, s.by0, s.by1);
    }
    for (std::size_t i = 0; i < s.items.size(); ++i) {
        if (!is_start[i] && !is_dest[i])
            continue;
        add_coord(xs, s.items[i].center.x, s.bx0, s.bx1);
        add_coord(ys, s.items[i].center.y, s.by0, s.by1);
    }
    cluster_coords(xs, tol, 1024);
    cluster_coords(ys, tol, 1024);
    if (xs.size() < 2 || ys.size() < 2)
        return false;
    const int nx = static_cast<int>(xs.size()) - 1;
    const int ny = static_cast<int>(ys.size()) - 1;
    std::vector<int> cell_rip(static_cast<std::size_t>(nx * ny), -1);
    std::vector<int32_t> cx(static_cast<std::size_t>(nx));
    std::vector<int32_t> cy(static_cast<std::size_t>(ny));
    for (int i = 0; i < nx; ++i)
        cx[static_cast<std::size_t>(i)] = (xs[static_cast<std::size_t>(i)] + xs[static_cast<std::size_t>(i + 1)]) / 2;
    for (int i = 0; i < ny; ++i)
        cy[static_cast<std::size_t>(i)] = (ys[static_cast<std::size_t>(i)] + ys[static_cast<std::size_t>(i + 1)]) / 2;
    struct Seg {
        int x0 = 0;
        int x1 = 0;
        int id = -1;
        bool hard = false;
    };
    std::vector<std::vector<Seg>> row_segs(static_cast<std::size_t>(ny));
    for (const Block& b : blocks) {
        int ix0;
        int ix1;
        int iy0;
        int iy1;
        // every cell the block overlaps, so clustered coordinates never open a room into it
        ix0 = static_cast<int>(std::upper_bound(xs.begin(), xs.end(), b.box.x0) - xs.begin()) - 1;
        if (ix0 < 0)
            ix0 = 0;
        ix1 = static_cast<int>(std::lower_bound(xs.begin(), xs.end(), b.box.x1) - xs.begin());
        iy0 = static_cast<int>(std::upper_bound(ys.begin(), ys.end(), b.box.y0) - ys.begin()) - 1;
        if (iy0 < 0)
            iy0 = 0;
        iy1 = static_cast<int>(std::lower_bound(ys.begin(), ys.end(), b.box.y1) - ys.begin());
        if (ix1 > nx)
            ix1 = nx;
        if (iy1 > ny)
            iy1 = ny;
        if (ix0 >= ix1 || iy0 >= iy1)
            continue;
        Seg seg;
        seg.x0 = ix0;
        seg.x1 = ix1;
        seg.hard = b.hard;
        seg.id = b.hard ? -2 : b.rip_item;
        for (int iy = iy0; iy < iy1; ++iy)
            row_segs[static_cast<std::size_t>(iy)].push_back(seg);
    }
    std::map<std::vector<int>, int> set_ids;
    struct Edge {
        int x = 0;
        int id = -1;
        bool open = false;
    };
    std::vector<Edge> edges;
    std::vector<int> active;
    std::vector<int> key;
    auto label = [&]() {
        key = active;
        std::sort(key.begin(), key.end());
        key.erase(std::unique(key.begin(), key.end()), key.end());
        if (key.size() == 1)
            return key.front();
        auto found = set_ids.find(key);
        if (found != set_ids.end())
            return found->second;
        int id = -3 - static_cast<int>(maze.rip_sets.size());
        maze.rip_sets.push_back(key);
        set_ids.emplace(key, id);
        return id;
    };
    for (int iy = 0; iy < ny; ++iy) {
        const std::vector<Seg>& segs = row_segs[static_cast<std::size_t>(iy)];
        if (segs.empty())
            continue;
        int* row = cell_rip.data() + static_cast<std::ptrdiff_t>(iy * nx);
        auto paint = [&](int x0, int x1, int id) {
            x0 = std::max(0, x0);
            x1 = std::min(nx, x1);
            if (x0 < x1)
                std::fill(row + x0, row + x1, id);
        };
        edges.clear();
        for (const Seg& seg : segs) {
            if (seg.hard)
                continue;
            edges.push_back(Edge{seg.x0, seg.id, true});
            edges.push_back(Edge{seg.x1, seg.id, false});
        }
        std::sort(edges.begin(), edges.end(), [](const Edge& a, const Edge& b) {
            return a.x != b.x ? a.x < b.x : (!a.open && b.open);
        });
        active.clear();
        for (std::size_t e = 0; e < edges.size();) {
            const int x = edges[e].x;
            for (; e < edges.size() && edges[e].x == x; ++e) {
                if (edges[e].open)
                    active.push_back(edges[e].id);
                else
                    active.erase(std::find(active.begin(), active.end(), edges[e].id));
            }
            if (!active.empty() && e < edges.size())
                paint(x, edges[e].x, label());
        }
        for (const Seg& seg : segs) {
            if (seg.hard)
                paint(seg.x0, seg.x1, -2);
        }
    }
    if (s.has_outline || edge_gap > 0) {
        const int64_t gap_lo = static_cast<int64_t>(s.bx0) + edge_gap;
        const int64_t gap_hi = static_cast<int64_t>(s.bx1) - edge_gap + 1;
        for (int iy = 0; iy < ny; ++iy) {
            int32_t y = cy[static_cast<std::size_t>(iy)];
            int* row_cells = cell_rip.data() + static_cast<std::ptrdiff_t>(iy * nx);
            if (y < s.by0 + edge_gap || y > s.by1 - edge_gap) {
                std::fill(row_cells, row_cells + nx, -2);
                continue;
            }
            // cells between two steps of the row share one answer
            BoardRow row(s, y);
            for (int ix = 0; ix < nx;) {
                int32_t x = cx[static_cast<std::size_t>(ix)];
                bool out = x < gap_lo || x >= gap_hi || (s.has_outline && !row.inside(x));
                int64_t next = s.has_outline ? row.next_step(x) : std::numeric_limits<int64_t>::max();
                if (x < gap_lo)
                    next = std::min(next, gap_lo);
                else if (x < gap_hi)
                    next = std::min(next, gap_hi);
                int ix2 = static_cast<int>(std::lower_bound(cx.begin() + ix + 1, cx.end(), next,
                    [](int32_t c, int64_t v) { return c < v; }) - cx.begin());
                if (out)
                    std::fill(row_cells + ix, row_cells + ix2, -2);
                ix = ix2;
            }
        }
    }
    std::vector<char> used(cell_rip.size(), 0);
    room_of_cell.assign(cell_rip.size(), -1);
    for (int iy = 0; iy < ny; ++iy) {
        int ix = 0;
        while (ix < nx) {
            int id = cell_rip[static_cast<std::size_t>(iy * nx + ix)];
            if (id == -2 || used[static_cast<std::size_t>(iy * nx + ix)]) {
                ++ix;
                continue;
            }
            int ix2 = ix + 1;
            while (ix2 < nx && !used[static_cast<std::size_t>(iy * nx + ix2)]
                && cell_rip[static_cast<std::size_t>(iy * nx + ix2)] == id)
                ++ix2;
            int iy2 = iy + 1;
            bool grow = true;
            while (grow && iy2 < ny) {
                for (int k = ix; k < ix2; ++k) {
                    if (used[static_cast<std::size_t>(iy2 * nx + k)]
                        || cell_rip[static_cast<std::size_t>(iy2 * nx + k)] != id) {
                        grow = false;
                        break;
                    }
                }
                if (grow)
                    ++iy2;
            }
            Room room;
            room.layer = layer;
            room.box = IBox{xs[static_cast<std::size_t>(ix)], ys[static_cast<std::size_t>(iy)],
                xs[static_cast<std::size_t>(ix2)], ys[static_cast<std::size_t>(iy2)]};
            room.rip_item = id;
            int room_index = static_cast<int>(maze.rooms.size());
            maze.rooms.push_back(room);
            for (int y = iy; y < iy2; ++y) {
                for (int x = ix; x < ix2; ++x) {
                    used[static_cast<std::size_t>(y * nx + x)] = 1;
                    room_of_cell[static_cast<std::size_t>(y * nx + x)] = room_index;
                }
            }
            ix = ix2;
        }
    }
    mark_terminals(s, maze, layer, is_start, false);
    mark_terminals(s, maze, layer, is_dest, true);
    return true;
}

void add_door(Maze& maze, int ra, int rb, int half_w)
{
    const Room& a = maze.rooms[static_cast<std::size_t>(ra)];
    const Room& b = maze.rooms[static_cast<std::size_t>(rb)];
    if (a.layer != b.layer)
        return;
    Door door;
    door.room_a = ra;
    door.room_b = rb;
    door.layer = a.layer;
    int32_t y0 = std::max(a.box.y0, b.box.y0);
    int32_t y1 = std::min(a.box.y1, b.box.y1);
    int32_t x0 = std::max(a.box.x0, b.box.x0);
    int32_t x1 = std::min(a.box.x1, b.box.x1);
    if (a.box.x1 == b.box.x0 || b.box.x1 == a.box.x0) {
        if (y1 - y0 <= 0)
            return;
        door.vertical = true;
        door.c = a.box.x1 == b.box.x0 ? a.box.x1 : b.box.x1;
        door.a0 = y0;
        door.a1 = y1;
    } else if (a.box.y1 == b.box.y0 || b.box.y1 == a.box.y0) {
        if (x1 - x0 <= 0)
            return;
        door.vertical = false;
        door.c = a.box.y1 == b.box.y0 ? a.box.y1 : b.box.y1;
        door.a0 = x0;
        door.a1 = x1;
    } else
        return;
    int32_t span = door.a1 - door.a0;
    int parts = span >= std::max(1, half_w) * 2 ? 2 : 1;
    door.sections.resize(static_cast<std::size_t>(parts));
    for (int i = 0; i < parts; ++i) {
        int32_t p0 = door.a0 + static_cast<int32_t>((static_cast<int64_t>(span) * i) / parts);
        int32_t p1 = door.a0 + static_cast<int32_t>((static_cast<int64_t>(span) * (i + 1)) / parts);
        int32_t mid = (p0 + p1) / 2;
        int32_t inset = std::min<int32_t>(std::max(1, half_w), (p1 - p0) / 2);
        Section& sec = door.sections[static_cast<std::size_t>(i)];
        sec.lo = std::min(mid, p0 + inset);
        sec.hi = std::max(mid, p1 - inset);
        sec.mid = door.vertical ? IPt{door.c, mid} : IPt{mid, door.c};
        sec.at = sec.mid;
    }
    maze.doors.push_back(std::move(door));
}

void link_doors(Maze& maze, int layer, int half_w)
{
    struct Edge {
        int32_t c = 0;
        int32_t a0 = 0;
        int32_t a1 = 0;
        int room = -1;
        bool vertical = false;
    };
    std::vector<Edge> edges;
    for (std::size_t i = 0; i < maze.rooms.size(); ++i) {
        if (maze.rooms[i].layer != layer)
            continue;
        const IBox& b = maze.rooms[i].box;
        if (b.x0 >= b.x1 || b.y0 >= b.y1)
            continue;
        edges.push_back(Edge{b.x0, b.y0, b.y1, static_cast<int>(i), true});
        edges.push_back(Edge{b.x1, b.y0, b.y1, static_cast<int>(i), true});
        edges.push_back(Edge{b.y0, b.x0, b.x1, static_cast<int>(i), false});
        edges.push_back(Edge{b.y1, b.x0, b.x1, static_cast<int>(i), false});
    }
    std::sort(edges.begin(), edges.end(), [](const Edge& a, const Edge& b) {
        if (a.vertical != b.vertical)
            return a.vertical > b.vertical;
        if (a.c != b.c)
            return a.c < b.c;
        return a.a0 < b.a0;
    });
    for (std::size_t i = 0; i < edges.size(); ++i) {
        for (std::size_t j = i + 1; j < edges.size(); ++j) {
            if (edges[j].vertical != edges[i].vertical || edges[j].c != edges[i].c)
                break;
            if (edges[j].a0 >= edges[i].a1)
                break;
            if (edges[j].room != edges[i].room)
                add_door(maze, edges[i].room, edges[j].room, half_w);
        }
    }
}

void build_drills(const Snap& s, Maze& maze, int net)
{
    maze.drills_at.assign(maze.rooms.size(), {});
    if (!s.vias_allowed || s.layers < 2)
        return;
    const int page = std::max(s.half_w * 20, 500);
    int cols = std::max(1, (s.bx1 - s.bx0) / page);
    int rows = std::max(1, (s.by1 - s.by0) / page);
    if (cols > 40)
        cols = 40;
    if (rows > 40)
        rows = 40;
    maze.pages.resize(static_cast<std::size_t>(cols * rows));
    for (int r = 0; r < rows; ++r) {
        for (int c = 0; c < cols; ++c) {
            Page& p = maze.pages[static_cast<std::size_t>(r * cols + c)];
            p.box.x0 = s.bx0 + static_cast<int32_t>((static_cast<int64_t>(s.bx1 - s.bx0) * c) / cols);
            p.box.x1 = s.bx0 + static_cast<int32_t>((static_cast<int64_t>(s.bx1 - s.bx0) * (c + 1)) / cols);
            p.box.y0 = s.by0 + static_cast<int32_t>((static_cast<int64_t>(s.by1 - s.by0) * r) / rows);
            p.box.y1 = s.by0 + static_cast<int32_t>((static_cast<int64_t>(s.by1 - s.by0) * (r + 1)) / rows);
        }
    }
    (void)net;
    const int gcols = 48;
    const int grows = 48;
    const int64_t span_x = std::max<int64_t>(1, static_cast<int64_t>(s.bx1) - s.bx0);
    const int64_t span_y = std::max<int64_t>(1, static_cast<int64_t>(s.by1) - s.by0);
    auto col_of = [&](int32_t x) {
        int col = static_cast<int>(((static_cast<int64_t>(x) - s.bx0) * gcols) / span_x);
        return std::min(gcols - 1, std::max(0, col));
    };
    auto row_of = [&](int32_t y) {
        int row = static_cast<int>(((static_cast<int64_t>(y) - s.by0) * grows) / span_y);
        return std::min(grows - 1, std::max(0, row));
    };
    const int via_sep = std::max(1, 2 * s.via_r + pair_clearance(s, s.via_clearance, s.via_clearance, 0));
    const int64_t sep2 = static_cast<int64_t>(via_sep) * via_sep;
    std::vector<std::vector<int>> placed(static_cast<std::size_t>(gcols * grows));
    auto drill_too_close = [&](int32_t x, int32_t y) {
        int reach_x = static_cast<int>((static_cast<int64_t>(via_sep) * gcols) / span_x) + 1;
        int reach_y = static_cast<int>((static_cast<int64_t>(via_sep) * grows) / span_y) + 1;
        int c0 = std::max(0, col_of(x) - reach_x);
        int c1 = std::min(gcols - 1, col_of(x) + reach_x);
        int r0 = std::max(0, row_of(y) - reach_y);
        int r1 = std::min(grows - 1, row_of(y) + reach_y);
        for (int r = r0; r <= r1; ++r) {
            for (int c = c0; c <= c1; ++c) {
                for (int di : placed[static_cast<std::size_t>(r * gcols + c)]) {
                    const IPt& at = maze.drills[static_cast<std::size_t>(di)].at;
                    int64_t dx = static_cast<int64_t>(x) - at.x;
                    int64_t dy = static_cast<int64_t>(y) - at.y;
                    if (dx * dx + dy * dy < sep2)
                        return true;
                }
            }
        }
        return false;
    };
    std::vector<std::vector<int>> on_layer(static_cast<std::size_t>(s.layers));
    for (std::size_t i = 0; i < maze.rooms.size(); ++i) {
        int layer = maze.rooms[i].layer;
        if (layer >= 0 && layer < s.layers)
            on_layer[static_cast<std::size_t>(layer)].push_back(static_cast<int>(i));
    }
    auto page_index = [&](int32_t x, int32_t y) {
        int col = std::min(cols - 1, std::max(0, static_cast<int>(((static_cast<int64_t>(x - s.bx0) * cols) / std::max(1, s.bx1 - s.bx0)))));
        int row = std::min(rows - 1, std::max(0, static_cast<int>(((static_cast<int64_t>(y - s.by0) * rows) / std::max(1, s.by1 - s.by0)))));
        return row * cols + col;
    };
    const int pitch = std::max(50, s.via_r / 2);
    int mcols = static_cast<int>((span_x + pitch - 1) / pitch) + 1;
    int mrows = static_cast<int>((span_y + pitch - 1) / pitch) + 1;
    if (mcols < 1)
        mcols = 1;
    if (mrows < 1)
        mrows = 1;
    std::vector<char> via_mask(static_cast<std::size_t>(mcols * mrows), 0);
    auto mcol = [&](int32_t x) {
        int c = static_cast<int>((static_cast<int64_t>(x - s.bx0)) / pitch);
        return std::min(mcols - 1, std::max(0, c));
    };
    auto mrow = [&](int32_t y) {
        int r = static_cast<int>((static_cast<int64_t>(y - s.by0)) / pitch);
        return std::min(mrows - 1, std::max(0, r));
    };
    auto mark_box = [&](int32_t x0, int32_t y0, int32_t x1, int32_t y1) {
        if (x1 < x0 || y1 < y0)
            return;
        int c0 = mcol(x0);
        int c1 = mcol(x1);
        int r0 = mrow(y0);
        int r1 = mrow(y1);
        for (int r = r0; r <= r1; ++r)
            std::fill(via_mask.begin() + static_cast<std::ptrdiff_t>(r * mcols + c0),
                via_mask.begin() + static_cast<std::ptrdiff_t>(r * mcols + c1 + 1), 1);
    };
    for (std::size_t i = 0; i < s.items.size(); ++i) {
        const SnapItem& it = s.items[i];
        if (it.kind == Kind::Plane || it.kind == Kind::Other)
            continue;
        if (it.kind == Kind::Trace && it.corners.size() >= 2) {
            int need = s.via_r + item_half_width(s, it.net, it.layer0) + pair_clearance(s, s.via_clearance, it.clearance, it.layer0);
            for (std::size_t k = 1; k < it.corners.size(); ++k) {
                const IPt& c = it.corners[k - 1];
                const IPt& d = it.corners[k];
                mark_box(std::min(c.x, d.x) - need, std::min(c.y, d.y) - need, std::max(c.x, d.x) + need, std::max(c.y, d.y) + need);
            }
        } else if (it.kind == Kind::Pin || it.kind == Kind::Via || it.kind == Kind::Keepout || it.kind == Kind::ViaKeepout) {
            int pad = s.via_r + pair_clearance(s, s.via_clearance, it.clearance, it.layer0);
            mark_box(it.box.x0 - pad, it.box.y0 - pad, it.box.x1 + pad, it.box.y1 + pad);
        }
    }
    auto mask_blocked = [&](int32_t x, int32_t y) {
        return via_mask[static_cast<std::size_t>(mrow(y) * mcols + mcol(x))] != 0;
    };
    std::vector<int> stamp(maze.rooms.size(), 0);
    int mark = 1;
    auto place_drill = [&](int layer, int r0, int r1) {
        const IBox& a = maze.rooms[static_cast<std::size_t>(r0)].box;
        const IBox& b = maze.rooms[static_cast<std::size_t>(r1)].box;
        if (!overlap(a, b))
            return;
        int32_t x0 = std::max(a.x0, b.x0);
        int32_t x1 = std::min(a.x1, b.x1);
        int32_t y0 = std::max(a.y0, b.y0);
        int32_t y1 = std::min(a.y1, b.y1);
        if (x1 <= x0 || y1 <= y0)
            return;
        int32_t x = (x0 + x1) / 2;
        int32_t y = (y0 + y1) / 2;
        if (!via_fits(s, x, y) || mask_blocked(x, y) || drill_too_close(x, y))
            return;
        Drill d;
        d.at = IPt{x, y};
        d.layer0 = layer;
        d.layer1 = layer + 1;
        d.room0 = r0;
        d.room1 = r1;
        int di = static_cast<int>(maze.drills.size());
        maze.drills.push_back(d);
        placed[static_cast<std::size_t>(row_of(y) * gcols + col_of(x))].push_back(di);
        maze.pages[static_cast<std::size_t>(page_index(x, y))].drills.push_back(di);
        maze.drills_at[static_cast<std::size_t>(r0)].push_back(di);
        maze.drills_at[static_cast<std::size_t>(r1)].push_back(di);
    };
    for (int layer = 0; layer + 1 < s.layers; ++layer) {
        std::vector<std::vector<int>> room_buckets(static_cast<std::size_t>(gcols * grows));
        for (int r1 : on_layer[static_cast<std::size_t>(layer + 1)]) {
            const IBox& b = maze.rooms[static_cast<std::size_t>(r1)].box;
            int c0 = col_of(b.x0);
            int c1 = col_of(b.x1);
            int r0 = row_of(b.y0);
            int r1c = row_of(b.y1);
            for (int r = r0; r <= r1c; ++r)
                for (int c = c0; c <= c1; ++c)
                    room_buckets[static_cast<std::size_t>(r * gcols + c)].push_back(r1);
        }
        for (int r0 : on_layer[static_cast<std::size_t>(layer)]) {
            if (++mark == 0) {
                std::fill(stamp.begin(), stamp.end(), 0);
                mark = 1;
            }
            auto consider = [&](int r1) {
                if (stamp[static_cast<std::size_t>(r1)] == mark)
                    return;
                stamp[static_cast<std::size_t>(r1)] = mark;
                place_drill(layer, r0, r1);
            };
            const IBox& a = maze.rooms[static_cast<std::size_t>(r0)].box;
            int c0 = col_of(a.x0);
            int c1 = col_of(a.x1);
            int y0 = row_of(a.y0);
            int y1 = row_of(a.y1);
            for (int r = y0; r <= y1; ++r) {
                for (int c = c0; c <= c1; ++c) {
                    for (int r1 : room_buckets[static_cast<std::size_t>(r * gcols + c)])
                        consider(r1);
                }
            }
        }
    }
}

struct WaveNode {
    double f = 0;
    double g = 0;
    uint64_t tie = 0;
    int kind = 0;
    int index = 0;
    int sec = 0;
    int from_door = -1;
    int from_sec = -1;
    int from_drill = -1;
    IPt at{};
};

struct WaveCmp {
    bool operator()(const WaveNode& a, const WaveNode& b) const
    {
        if (a.f != b.f)
            return a.f > b.f;
        return a.tie > b.tie;
    }
};

double dist_point(IPt a, IPt b, double ch, double cv)
{
    return std::abs(a.x - b.x) * ch + std::abs(a.y - b.y) * cv;
}

Found search_wave(Snap& s, Maze& maze, int net, int half_w, std::chrono::steady_clock::time_point deadline,
    const std::function<bool()>& stop)
{
    Found found;
    // like DestinationDistance: estimate against the box of all destination points
    IBox goal_box{0, 0, 0, 0};
    bool have_goal = false;
    for (const Room& room : maze.rooms) {
        if (!room.dest)
            continue;
        IPt g = room.has_goal ? room.goal : IPt{(room.box.x0 + room.box.x1) / 2, (room.box.y0 + room.box.y1) / 2};
        if (!have_goal)
            goal_box = IBox{g.x, g.y, g.x, g.y};
        goal_box.x0 = std::min(goal_box.x0, g.x);
        goal_box.y0 = std::min(goal_box.y0, g.y);
        goal_box.x1 = std::max(goal_box.x1, g.x);
        goal_box.y1 = std::max(goal_box.y1, g.y);
        have_goal = true;
    }
    auto to_goal = [&](IPt p, double ch, double cv) {
        if (!have_goal)
            return 0.0;
        IPt q{std::min(std::max(p.x, goal_box.x0), goal_box.x1), std::min(std::max(p.y, goal_box.y0), goal_box.y1)};
        return dist_point(p, q, ch, cv);
    };
    auto room_cost = [&](const Room& room, double& ch, double& cv) {
        ch = s.cost_h[static_cast<std::size_t>(clamp_layer(room.layer, s.layers))];
        cv = s.cost_v[static_cast<std::size_t>(clamp_layer(room.layer, s.layers))];
    };
    if (!have_goal && !s.fanout)
        return found;
    std::vector<std::vector<int>> doors_at(maze.rooms.size());
    for (std::size_t di = 0; di < maze.doors.size(); ++di) {
        doors_at[static_cast<std::size_t>(maze.doors[di].room_a)].push_back(static_cast<int>(di));
        doors_at[static_cast<std::size_t>(maze.doors[di].room_b)].push_back(static_cast<int>(di));
    }
    std::priority_queue<WaveNode, std::vector<WaveNode>, WaveCmp> heap;
    std::vector<double> best_door(maze.doors.size() * 2, std::numeric_limits<double>::infinity());
    std::vector<double> best_drill(maze.drills.size(), std::numeric_limits<double>::infinity());
    uint64_t tie = 1;
    // the entry point is the point of the section nearest to where the wave comes from
    auto push_door = [&](int door, int sec, double g_base, IPt from, int from_door, int from_sec, int from_drill) {
        Door& d = maze.doors[static_cast<std::size_t>(door)];
        if (sec < 0 || sec >= static_cast<int>(d.sections.size()) || sec >= 2)
            return;
        const Section& target = d.sections[static_cast<std::size_t>(sec)];
        if (target.occupied)
            return;
        IPt entry = d.vertical ? IPt{d.c, std::min(std::max(from.y, target.lo), target.hi)}
                               : IPt{std::min(std::max(from.x, target.lo), target.hi), d.c};
        double ch = s.cost_h[static_cast<std::size_t>(clamp_layer(d.layer, s.layers))];
        double cv = s.cost_v[static_cast<std::size_t>(clamp_layer(d.layer, s.layers))];
        double g = g_base + dist_point(from, entry, ch, cv);
        double& best = best_door[static_cast<std::size_t>(door) * 2 + static_cast<std::size_t>(sec)];
        if (g >= best)
            return;
        best = g;
        double h = to_goal(entry, ch, cv);
        WaveNode n;
        n.at = entry;
        n.g = g;
        n.f = g + h;
        n.tie = tie++;
        n.kind = 0;
        n.index = door;
        n.sec = sec;
        n.from_door = from_door;
        n.from_sec = from_sec;
        n.from_drill = from_drill;
        heap.push(n);
    };
    for (std::size_t di = 0; di < maze.doors.size(); ++di) {
        const Door& d = maze.doors[di];
        for (std::size_t sec = 0; sec < d.sections.size(); ++sec) {
            for (int ri : {d.room_a, d.room_b}) {
                const Room& room = maze.rooms[static_cast<std::size_t>(ri)];
                if (!room.start)
                    continue;
                if (room.has_start) {
                    double ch = 1;
                    double cv = 1;
                    room_cost(room, ch, cv);
                    push_door(static_cast<int>(di), static_cast<int>(sec), dist_point(room.start_at, room.start_entry, ch, cv),
                        room.start_entry, -1, -1, -1);
                } else
                    push_door(static_cast<int>(di), static_cast<int>(sec), 0, d.sections[sec].mid, -1, -1, -1);
            }
        }
    }
    auto push_goal = [&](int room_i, double g, int from_door, int from_sec, int from_drill, IPt from) {
        const Room& room = maze.rooms[static_cast<std::size_t>(room_i)];
        double leg = 0;
        if (room.has_goal) {
            double ch = 1;
            double cv = 1;
            room_cost(room, ch, cv);
            leg = dist_point(from, room.goal_entry, ch, cv) + dist_point(room.goal_entry, room.goal, ch, cv);
        }
        WaveNode n;
        n.g = g + leg;
        n.f = n.g;
        n.tie = tie++;
        n.kind = 2;
        n.index = room_i;
        n.from_door = from_door;
        n.from_sec = from_sec;
        n.from_drill = from_drill;
        heap.push(n);
    };
    auto push_drill = [&](int drill_i, double g, int from_door, int from_sec) {
        if (drill_i < 0 || drill_i >= static_cast<int>(maze.drills.size()))
            return;
        if (maze.drills[static_cast<std::size_t>(drill_i)].occupied)
            return;
        double& best = best_drill[static_cast<std::size_t>(drill_i)];
        if (g >= best)
            return;
        best = g;
        double h = to_goal(maze.drills[static_cast<std::size_t>(drill_i)].at, 1, 1);
        WaveNode n;
        n.g = g;
        n.f = g + h;
        n.tie = tie++;
        n.kind = 1;
        n.index = drill_i;
        n.from_door = from_door;
        n.from_sec = from_sec;
        heap.push(n);
    };
    int hit_door = -1;
    int hit_sec = -1;
    int hit_drill = -1;
    int hit_room = -1;
    int spins = 0;
    while (!heap.empty()) {
        if ((++spins & 255) == 0)
            note_paint();
        if (stop() || std::chrono::steady_clock::now() > deadline)
            return found;
        WaveNode cur = heap.top();
        heap.pop();
        if (cur.kind == 2) {
            const Room& landed = maze.rooms[static_cast<std::size_t>(cur.index)];
            hit_room = cur.index;
            if (cur.from_drill >= 0)
                hit_drill = cur.from_drill;
            else {
                hit_door = cur.from_door;
                hit_sec = cur.from_sec;
            }
            if (landed.has_goal) {
                found.has_goal = true;
                found.goal = landed.goal;
                found.goal_entry = landed.goal_entry;
                found.goal_layer = landed.layer;
            }
            break;
        }
        if (cur.kind == 1) {
            Drill& drill = maze.drills[static_cast<std::size_t>(cur.index)];
            if (drill.occupied || cur.g > best_drill[static_cast<std::size_t>(cur.index)])
                continue;
            drill.occupied = true;
            drill.back_door = cur.from_door;
            drill.back_sec = cur.from_sec;
            if (s.fanout && cur.from_door >= 0) {
                hit_drill = cur.index;
                break;
            }
            int rooms[2] = {drill.room0, drill.room1};
            for (int room : rooms) {
                Room& landed = maze.rooms[static_cast<std::size_t>(room)];
                if (landed.dest && !s.fanout) {
                    push_goal(room, cur.g, -1, -1, cur.index, drill.at);
                    continue;
                }
                for (int di : doors_at[static_cast<std::size_t>(room)]) {
                    const Door& d = maze.doors[static_cast<std::size_t>(di)];
                    for (std::size_t sec = 0; sec < d.sections.size(); ++sec)
                        push_door(static_cast<int>(di), static_cast<int>(sec), cur.g + s.via_cost, drill.at, -1, -1, cur.index);
                }
            }
            continue;
        }
        Door& door = maze.doors[static_cast<std::size_t>(cur.index)];
        Section& sec = door.sections[static_cast<std::size_t>(cur.sec)];
        if (sec.occupied || cur.g > best_door[static_cast<std::size_t>(cur.index) * 2 + static_cast<std::size_t>(cur.sec)])
            continue;
        sec.occupied = true;
        sec.at = cur.at;
        sec.back_door = cur.from_door;
        sec.back_sec = cur.from_sec;
        if (cur.from_drill >= 0) {
            sec.back_door = -2;
            sec.back_sec = cur.from_drill;
        }
        int rooms[2] = {door.room_a, door.room_b};
        for (int room_i : rooms) {
            Room& room = maze.rooms[static_cast<std::size_t>(room_i)];
            const std::pair<const int*, int> rips = maze.rip_span(room.rip_item);
            bool forbidden = false;
            for (int k = 0; k < rips.second; ++k) {
                const int item = rips.first[k];
                forbidden = forbidden || (item < static_cast<int>(s.forbid_rip.size()) && s.forbid_rip[static_cast<std::size_t>(item)] != 0);
            }
            if (forbidden)
                continue;
            double extra = 0;
            if (rips.second > 0) {
                // like MazeSearchAlgo.check_ripup: moving on inside the same ripped item costs nothing
                const int prev_room = door.room_a == room_i ? door.room_b : door.room_a;
                const std::pair<const int*, int> before = maze.rip_span(maze.rooms[static_cast<std::size_t>(prev_room)].rip_item);
                for (int k = 0; k < rips.second; ++k) {
                    const int item = rips.first[k];
                    if (std::find(before.first, before.first + before.second, item) != before.first + before.second)
                        continue;
                    extra += item < static_cast<int>(s.rip_cost.size()) ? s.rip_cost[static_cast<std::size_t>(item)] : s.ripup_cost;
                }
                sec.ripped = true;
                sec.rip_item = room.rip_item;
            }
            if (room.dest && !s.fanout) {
                push_goal(room_i, cur.g + extra, cur.index, cur.sec, -1, sec.at);
                continue;
            }
            for (int di : doors_at[static_cast<std::size_t>(room_i)]) {
                if (di == cur.index)
                    continue;
                const Door& next = maze.doors[static_cast<std::size_t>(di)];
                for (std::size_t ns = 0; ns < next.sections.size(); ++ns)
                    push_door(static_cast<int>(di), static_cast<int>(ns), cur.g + extra, sec.at, cur.index, cur.sec, -1);
            }
            if (s.vias_allowed && room_i < static_cast<int>(maze.drills_at.size())) {
                for (int drill_i : maze.drills_at[static_cast<std::size_t>(room_i)]) {
                    const Drill& drill = maze.drills[static_cast<std::size_t>(drill_i)];
                    double step = s.via_cost + dist_point(sec.at, drill.at, 1, 1);
                    push_drill(drill_i, cur.g + step, cur.index, cur.sec);
                }
            }
        }
    }
    if (hit_door < 0 && hit_drill < 0)
        return found;
    auto note_rip = [&](int room) {
        if (room < 0 || room >= static_cast<int>(maze.rooms.size()))
            return;
        const std::pair<const int*, int> rips = maze.rip_span(maze.rooms[static_cast<std::size_t>(room)].rip_item);
        for (int k = 0; k < rips.second; ++k) {
            if (std::find(found.rip_items.begin(), found.rip_items.end(), rips.first[k]) == found.rip_items.end())
                found.rip_items.push_back(rips.first[k]);
        }
    };
    int at_room = -1;
    if (hit_door >= 0 && hit_room >= 0)
        at_room = hit_room;
    else if (hit_door >= 0) {
        const Door& door = maze.doors[static_cast<std::size_t>(hit_door)];
        if (maze.rooms[static_cast<std::size_t>(door.room_a)].dest)
            at_room = door.room_a;
        else if (maze.rooms[static_cast<std::size_t>(door.room_b)].dest)
            at_room = door.room_b;
        else
            at_room = door.room_a;
    }
    note_rip(at_room);
    std::vector<Step> rev;
    if (hit_drill >= 0 && hit_door < 0) {
        const Drill& entered = maze.drills[static_cast<std::size_t>(hit_drill)];
        note_rip(entered.room0);
        note_rip(entered.room1);
        if (hit_room >= 0)
            at_room = entered.room0 == hit_room ? entered.room1 : entered.room0;
        else if (entered.room0 >= 0 && maze.rooms[static_cast<std::size_t>(entered.room0)].dest)
            at_room = entered.room1;
        else
            at_room = entered.room0;
        Step st;
        st.type = Step::Drill;
        st.drill = hit_drill;
        rev.push_back(st);
        hit_door = entered.back_door;
        hit_sec = entered.back_sec;
    }
    int guard = 0;
    while (hit_door >= 0 && guard++ < 100000) {
        Step st;
        st.type = Step::Door;
        st.door = hit_door;
        st.sec = hit_sec;
        rev.push_back(st);
        Door& door = maze.doors[static_cast<std::size_t>(hit_door)];
        Section& sec = door.sections[static_cast<std::size_t>(hit_sec)];
        int other = door.room_a == at_room ? door.room_b : door.room_a;
        note_rip(other);
        at_room = other;
        if (sec.back_door == -2) {
            Step via;
            via.type = Step::Drill;
            via.drill = sec.back_sec;
            rev.push_back(via);
            Drill& drill = maze.drills[static_cast<std::size_t>(sec.back_sec)];
            int came = drill.room0 == at_room ? drill.room1 : drill.room0;
            note_rip(came);
            at_room = came;
            found.has_via = true;
            found.via_x = drill.at.x;
            found.via_y = drill.at.y;
            found.via_layer0 = drill.layer0;
            found.via_layer1 = drill.layer1;
            hit_door = drill.back_door;
            hit_sec = drill.back_sec;
            continue;
        }
        int prev_d = sec.back_door;
        int prev_s = sec.back_sec;
        hit_door = prev_d;
        hit_sec = prev_s;
    }
    if (at_room >= 0 && at_room < static_cast<int>(maze.rooms.size())) {
        const Room& first = maze.rooms[static_cast<std::size_t>(at_room)];
        if (first.start && first.has_start) {
            found.has_start = true;
            found.start_at = first.start_at;
            found.start_entry = first.start_entry;
        }
    }
    std::reverse(rev.begin(), rev.end());
    int layer = 0;
    if (!rev.empty() && rev.front().type == Step::Door)
        layer = maze.doors[static_cast<std::size_t>(rev.front().door)].layer;
    IPt pending_at{0, 0};
    bool pending_drill = false;
    for (const Step& st : rev) {
        if (st.type == Step::Drill) {
            const Drill& drill = maze.drills[static_cast<std::size_t>(st.drill)];
            int incoming = found.pt_layer.empty() ? drill.layer0 : found.pt_layer.back();
            if (incoming != drill.layer0 && incoming != drill.layer1)
                incoming = drill.layer0;
            found.pts.push_back(drill.at);
            found.pt_layer.push_back(incoming);
            pending_at = drill.at;
            pending_drill = true;
            found.has_via = true;
            found.via_x = drill.at.x;
            found.via_y = drill.at.y;
            continue;
        }
        const Section& sec = maze.doors[static_cast<std::size_t>(st.door)].sections[static_cast<std::size_t>(st.sec)];
        layer = maze.doors[static_cast<std::size_t>(st.door)].layer;
        if (pending_drill && (found.pt_layer.empty() || layer != found.pt_layer.back())) {
            found.pts.push_back(pending_at);
            found.pt_layer.push_back(layer);
            pending_drill = false;
        }
        found.pts.push_back(sec.at);
        found.pt_layer.push_back(layer);
    }
    found.layer = layer;
    if (found.pts.empty() && hit_door >= 0) {
        const Door& door = maze.doors[static_cast<std::size_t>(hit_door)];
        const Room& room = maze.rooms[static_cast<std::size_t>(door.room_a)];
        found.pts.push_back(IPt{(room.box.x0 + room.box.x1) / 2, (room.box.y0 + room.box.y1) / 2});
        found.pts.push_back(door.sections[static_cast<std::size_t>(std::max(0, hit_sec))].at);
        found.pt_layer.push_back(door.layer);
        found.pt_layer.push_back(door.layer);
        found.layer = door.layer;
    }
    found.ok = found.pts.size() >= 1 || found.has_via || hit_door >= 0 || hit_drill >= 0;
    return found;
}

void append_unique(std::vector<IPt>& pts, IPt p)
{
    if (!pts.empty() && pts.back().x == p.x && pts.back().y == p.y)
        return;
    pts.push_back(p);
}

template <typename Blocked>
std::vector<IPt> miter_polyline(const std::vector<IPt>& pts, Blocked blocked)
{
    std::vector<IPt> out;
    if (pts.size() < 3)
        return pts;
    append_unique(out, pts.front());
    for (std::size_t i = 1; i + 1 < pts.size(); ++i) {
        IPt prev = out.back();
        IPt corner = pts[i];
        IPt next = pts[i + 1];
        bool in_h = prev.y == corner.y && prev.x != corner.x;
        bool in_v = prev.x == corner.x && prev.y != corner.y;
        bool out_h = corner.y == next.y && corner.x != next.x;
        bool out_v = corner.x == next.x && corner.y != next.y;
        int32_t in_len = std::max(std::abs(corner.x - prev.x), std::abs(corner.y - prev.y));
        int32_t out_len = std::max(std::abs(next.x - corner.x), std::abs(next.y - corner.y));
        // the in-leg is already shortened by the previous cut; the out-leg is shared with the next corner
        const bool last = i + 2 == pts.size();
        int32_t limit = std::min(in_len, last ? out_len : out_len / 2);
        int32_t cut = limit;
        bool placed = false;
        if (cut >= 1 && ((in_h && out_v) || (in_v && out_h))) {
            auto ends = [&](int32_t c) {
                int32_t sx = corner.x == prev.x ? 0 : (corner.x > prev.x ? c : -c);
                int32_t sy = corner.y == prev.y ? 0 : (corner.y > prev.y ? c : -c);
                int32_t dx = next.x == corner.x ? 0 : (next.x > corner.x ? c : -c);
                int32_t dy = next.y == corner.y ? 0 : (next.y > corner.y ? c : -c);
                return std::make_pair(IPt{corner.x - sx, corner.y - sy}, IPt{corner.x + dx, corner.y + dy});
            };
            auto free_cut = [&](int32_t c) {
                auto e = ends(c);
                return !blocked(e.first, e.second);
            };
            int32_t best = 0;
            if (free_cut(cut))
                best = cut;
            else {
                int32_t lo = 0;
                int32_t hi = cut;
                while (hi - lo > 1) {
                    int32_t mid = lo + (hi - lo) / 2;
                    if (free_cut(mid))
                        lo = mid;
                    else
                        hi = mid;
                }
                best = lo;
            }
            if (best >= 1) {
                auto e = ends(best);
                append_unique(out, e.first);
                append_unique(out, e.second);
                placed = true;
            }
        }
        if (!placed)
            append_unique(out, corner);
    }
    append_unique(out, pts.back());
    return out;
}

std::vector<IPt> orthogonalize(const std::vector<IPt>& in, int angle)
{
    std::vector<IPt> pts;
    if (in.empty())
        return pts;
    append_unique(pts, in.front());
    for (std::size_t i = 1; i < in.size(); ++i) {
        IPt a = pts.back();
        IPt b = in[i];
        if (a.x == b.x || a.y == b.y || angle == 2) {
            append_unique(pts, b);
            continue;
        }
        IPt mid{b.x, a.y};
        append_unique(pts, mid);
        append_unique(pts, b);
    }
    return pts;
}

bool angle_ok(IPt a, IPt b, int angle)
{
    int32_t dx = std::abs(a.x - b.x);
    int32_t dy = std::abs(a.y - b.y);
    if (dx == 0 || dy == 0)
        return true;
    if (angle >= 2)
        return true;
    return angle == 1 && dx == dy;
}

bool proper_cross(IPt a, IPt b, IPt c, IPt d)
{
    if ((a.x == c.x && a.y == c.y) || (a.x == d.x && a.y == d.y) || (b.x == c.x && b.y == c.y) || (b.x == d.x && b.y == d.y))
        return false;
    auto orient = [](IPt p, IPt q, IPt r) {
        int64_t v = static_cast<int64_t>(q.x - p.x) * (r.y - p.y) - static_cast<int64_t>(q.y - p.y) * (r.x - p.x);
        return (v > 0) - (v < 0);
    };
    return orient(a, b, c) != orient(a, b, d) && orient(c, d, a) != orient(c, d, b);
}

void dedup_ortho(std::vector<IPt>& path)
{
    std::vector<IPt> slim;
    for (const IPt& p : path) {
        if (!slim.empty() && slim.back().x == p.x && slim.back().y == p.y)
            continue;
        if (slim.size() >= 2) {
            IPt a = slim[slim.size() - 2];
            IPt b = slim.back();
            if ((a.x == b.x && b.x == p.x) || (a.y == b.y && b.y == p.y)) {
                slim.back() = p;
                continue;
            }
        }
        slim.push_back(p);
    }
    path.swap(slim);
}

int64_t ortho_length(const std::vector<IPt>& path)
{
    int64_t sum = 0;
    for (std::size_t i = 1; i < path.size(); ++i) {
        sum += std::abs(static_cast<int64_t>(path[i].x) - path[i - 1].x);
        sum += std::abs(static_cast<int64_t>(path[i].y) - path[i - 1].y);
    }
    return sum;
}

bool jog_blocked(const Snap& s, int layer, int net, int margin, IPt a, IPt b, const std::vector<int>& ignore)
{
    if (!inside_board(s, a.x, a.y) || !inside_board(s, b.x, b.y))
        return true;
    if (near_edge(s, a, b, margin + s.edge_cl + 1))
        return true;
    struct Obs {
        int32_t x0 = 0;
        int32_t y0 = 0;
        int32_t x1 = 0;
        int32_t y1 = 0;
        int32_t ax = 0;
        int32_t ay = 0;
        int32_t bx = 0;
        int32_t by = 0;
        int need = 0;
        bool area = false;
    };
    struct Index {
        const Snap* snap = nullptr;
        int layer = -1;
        int net = -2;
        int margin = -1;
        int generation = -1;
        int ignore0 = -2;
        int ignore_n = -1;
        int g = 64;
        std::vector<std::vector<int>> cells;
        std::vector<int> wide;
        std::vector<Obs> obs;
        std::vector<int> stamp;
        int ticket = 1;
    };
    static Index ix;
    int ignore0 = ignore.empty() ? -1 : ignore[0];
    if (ix.snap != &s || ix.layer != layer || ix.net != net || ix.margin != margin || ix.generation != s.version
        || ix.ignore0 != ignore0 || ix.ignore_n != static_cast<int>(ignore.size())) {
        ix.snap = &s;
        ix.layer = layer;
        ix.net = net;
        ix.margin = margin;
        ix.generation = s.version;
        ix.ignore0 = ignore0;
        ix.ignore_n = static_cast<int>(ignore.size());
        ix.cells.assign(static_cast<std::size_t>(ix.g * ix.g), {});
        ix.wide.clear();
        ix.obs.clear();
        const int64_t span_x = std::max<int64_t>(1, static_cast<int64_t>(s.bx1) - s.bx0);
        const int64_t span_y = std::max<int64_t>(1, static_cast<int64_t>(s.by1) - s.by0);
        auto col_of = [&](int32_t x) {
            int col = static_cast<int>(((static_cast<int64_t>(x) - s.bx0) * ix.g) / span_x);
            return std::min(ix.g - 1, std::max(0, col));
        };
        auto row_of = [&](int32_t y) {
            int row = static_cast<int>(((static_cast<int64_t>(y) - s.by0) * ix.g) / span_y);
            return std::min(ix.g - 1, std::max(0, row));
        };
        auto skipped = [&](int idx) {
            return std::find(ignore.begin(), ignore.end(), idx) != ignore.end();
        };
        auto place = [&](const Obs& ob) {
            int id = static_cast<int>(ix.obs.size());
            ix.obs.push_back(ob);
            int c0 = col_of(ob.x0);
            int c1 = col_of(ob.x1);
            int r0 = row_of(ob.y0);
            int r1 = row_of(ob.y1);
            if ((c1 - c0 + 1) * (r1 - r0 + 1) > 400) {
                ix.wide.push_back(id);
                return;
            }
            for (int r = r0; r <= r1; ++r)
                for (int c = c0; c <= c1; ++c)
                    ix.cells[static_cast<std::size_t>(r * ix.g + c)].push_back(id);
        };
        for (std::size_t i = 0; i < s.items.size(); ++i) {
            if (skipped(static_cast<int>(i)))
                continue;
            const SnapItem& it = s.items[i];
            if (!on_layer(it, layer) || it.kind == Kind::Plane)
                continue;
            if (it.net == net && it.net > 0 && it.kind != Kind::Keepout)
                continue;
            if (it.kind != Kind::Keepout && !it.hard && !it.fixed && it.kind != Kind::Pin && it.kind != Kind::Via && it.kind != Kind::Trace)
                continue;
            int pad = margin + pair_clearance(s, 1, it.clearance, layer);
            if (it.kind == Kind::Trace && it.corners.size() >= 2) {
                int need = pad + item_half_width(s, it.net, layer);
                for (std::size_t k = 1; k < it.corners.size(); ++k) {
                    IPt c = it.corners[k - 1];
                    IPt d = it.corners[k];
                    Obs ob;
                    ob.ax = c.x;
                    ob.ay = c.y;
                    ob.bx = d.x;
                    ob.by = d.y;
                    ob.x0 = std::min(c.x, d.x) - need;
                    ob.y0 = std::min(c.y, d.y) - need;
                    ob.x1 = std::max(c.x, d.x) + need;
                    ob.y1 = std::max(c.y, d.y) + need;
                    ob.need = need;
                    ob.area = false;
                    place(ob);
                }
            } else {
                Obs ob;
                ob.x0 = it.box.x0 - pad;
                ob.y0 = it.box.y0 - pad;
                ob.x1 = it.box.x1 + pad;
                ob.y1 = it.box.y1 + pad;
                if (it.kind == Kind::Keepout) {
                    ob.x0 += 1;
                    ob.y0 += 1;
                    ob.x1 -= 1;
                    ob.y1 -= 1;
                    if (ob.x1 < ob.x0 || ob.y1 < ob.y0)
                        continue;
                }
                ob.area = true;
                place(ob);
            }
        }
        ix.stamp.assign(ix.obs.size(), 0);
        ix.ticket = 1;
    }
    auto hits_area = [&](const Obs& ob) {
        if (a.y == b.y)
            return a.y >= ob.y0 && a.y <= ob.y1 && std::max(a.x, b.x) >= ob.x0 && std::min(a.x, b.x) <= ob.x1;
        if (a.x == b.x)
            return a.x >= ob.x0 && a.x <= ob.x1 && std::max(a.y, b.y) >= ob.y0 && std::min(a.y, b.y) <= ob.y1;
        return false;
    };
    auto hits_trace = [&](const Obs& ob) {
        if (std::max(a.x, b.x) < ob.x0 || std::min(a.x, b.x) > ob.x1 || std::max(a.y, b.y) < ob.y0 || std::min(a.y, b.y) > ob.y1)
            return false;
        IPt c{ob.ax, ob.ay};
        IPt d{ob.bx, ob.by};
        double lim = static_cast<double>(ob.need) * static_cast<double>(ob.need);
        if (dist2_seg(c, d, a.x, a.y) < lim || dist2_seg(c, d, b.x, b.y) < lim)
            return true;
        if (dist2_seg(a, b, c.x, c.y) < lim || dist2_seg(a, b, d.x, d.y) < lim)
            return true;
        return proper_cross(a, b, c, d);
    };
    auto consider = [&](int id) {
        if (id < 0 || static_cast<std::size_t>(id) >= ix.obs.size())
            return false;
        if (ix.stamp[static_cast<std::size_t>(id)] == ix.ticket)
            return false;
        ix.stamp[static_cast<std::size_t>(id)] = ix.ticket;
        const Obs& ob = ix.obs[static_cast<std::size_t>(id)];
        return ob.area ? hits_area(ob) : hits_trace(ob);
    };
    if (++ix.ticket == std::numeric_limits<int>::max()) {
        std::fill(ix.stamp.begin(), ix.stamp.end(), 0);
        ix.ticket = 1;
    }
    for (int id : ix.wide) {
        if (consider(id))
            return true;
    }
    const int64_t span_x = std::max<int64_t>(1, static_cast<int64_t>(s.bx1) - s.bx0);
    const int64_t span_y = std::max<int64_t>(1, static_cast<int64_t>(s.by1) - s.by0);
    auto col_of = [&](int32_t x) {
        int col = static_cast<int>(((static_cast<int64_t>(x) - s.bx0) * ix.g) / span_x);
        return std::min(ix.g - 1, std::max(0, col));
    };
    auto row_of = [&](int32_t y) {
        int row = static_cast<int>(((static_cast<int64_t>(y) - s.by0) * ix.g) / span_y);
        return std::min(ix.g - 1, std::max(0, row));
    };
    int c0 = std::min(col_of(a.x), col_of(b.x));
    int c1 = std::max(col_of(a.x), col_of(b.x));
    int r0 = std::min(row_of(a.y), row_of(b.y));
    int r1 = std::max(row_of(a.y), row_of(b.y));
    for (int r = r0; r <= r1; ++r) {
        for (int c = c0; c <= c1; ++c) {
            for (int id : ix.cells[static_cast<std::size_t>(r * ix.g + c)]) {
                if (consider(id))
                    return true;
            }
        }
    }
    return false;
}

bool is_anchor(const Snap& s, IPt p)
{
    static const Snap* snap = nullptr;
    static int generation = -1;
    static std::unordered_set<uint64_t> keys;
    if (snap != &s || generation != s.version) {
        snap = &s;
        generation = s.version;
        keys.clear();
        for (const SnapItem& it : s.items) {
            if (it.kind != Kind::Pin && it.kind != Kind::Via)
                continue;
            uint64_t key = (static_cast<uint64_t>(static_cast<uint32_t>(it.center.x)) << 32)
                | static_cast<uint32_t>(it.center.y);
            keys.insert(key);
        }
    }
    uint64_t key = (static_cast<uint64_t>(static_cast<uint32_t>(p.x)) << 32) | static_cast<uint32_t>(p.y);
    return keys.find(key) != keys.end();
}

std::vector<IPt> collapse_jogs(const Snap& s, int layer, int net, int margin, const std::vector<IPt>& in, const std::vector<int>& ignore)
{
    std::vector<IPt> pts = in;
    dedup_ortho(pts);
    auto ortho = [](IPt a, IPt b) { return a.x == b.x || a.y == b.y; };
    auto perp = [](IPt a, IPt b, IPt c) {
        int64_t dx1 = static_cast<int64_t>(b.x) - a.x;
        int64_t dy1 = static_cast<int64_t>(b.y) - a.y;
        int64_t dx2 = static_cast<int64_t>(c.x) - b.x;
        int64_t dy2 = static_cast<int64_t>(c.y) - b.y;
        return dx1 * dx2 + dy1 * dy2 == 0 && (dx1 != 0 || dy1 != 0) && (dx2 != 0 || dy2 != 0);
    };
    auto overlaps = [](IPt a, IPt b, IPt c, IPt d) {
        if (a.y == b.y && c.y == d.y && a.y == c.y) {
            int32_t a0 = std::min(a.x, b.x);
            int32_t a1 = std::max(a.x, b.x);
            int32_t c0 = std::min(c.x, d.x);
            int32_t c1 = std::max(c.x, d.x);
            return std::min(a1, c1) > std::max(a0, c0);
        }
        if (a.x == b.x && c.x == d.x && a.x == c.x) {
            int32_t a0 = std::min(a.y, b.y);
            int32_t a1 = std::max(a.y, b.y);
            int32_t c0 = std::min(c.y, d.y);
            int32_t c1 = std::max(c.y, d.y);
            return std::min(a1, c1) > std::max(a0, c0);
        }
        return false;
    };
    auto sign_of = [](int32_t d) { return d > 0 ? 1 : (d < 0 ? -1 : 0); };
    bool changed = true;
    int guard = 0;
    while (changed && pts.size() >= 4 && guard < 4) {
        ++guard;
        changed = false;
        for (std::size_t i = 0; i + 3 < pts.size();) {
            IPt a0 = pts[i];
            IPt b0 = pts[i + 1];
            IPt c0 = pts[i + 2];
            IPt d0 = pts[i + 3];
            if (!ortho(a0, b0) || !ortho(b0, c0) || !ortho(c0, d0) || !perp(a0, b0, c0) || !perp(b0, c0, d0)) {
                ++i;
                continue;
            }
            if (is_anchor(s, b0) || is_anchor(s, c0)) {
                ++i;
                continue;
            }
            int hs = 0;
            int vs = 0;
            auto acc = [&](IPt p, IPt q) {
                int sx = sign_of(q.x - p.x);
                int sy = sign_of(q.y - p.y);
                if (sx != 0) {
                    if (hs != 0 && hs != sx)
                        return false;
                    hs = sx;
                }
                if (sy != 0) {
                    if (vs != 0 && vs != sy)
                        return false;
                    vs = sy;
                }
                return true;
            };
            bool mono = acc(a0, b0) && acc(b0, c0) && acc(c0, d0) && hs != 0 && vs != 0;
            std::size_t far = i + 3;
            if (mono) {
                for (std::size_t k = i + 4; k < pts.size() && k - i <= 48; ++k) {
                    IPt p = pts[k - 1];
                    IPt q = pts[k];
                    if (is_anchor(s, p) || !ortho(p, q) || !perp(pts[k - 2], p, q) || !acc(p, q))
                        break;
                    far = k;
                    if (is_anchor(s, q))
                        break;
                }
            }
            bool spliced = false;
            for (std::size_t j = far; j >= i + 3; --j) {
                IPt a = pts[i];
                IPt d = pts[j];
                int64_t old_len = 0;
                for (std::size_t k = i + 1; k <= j; ++k)
                    old_len += std::abs(static_cast<int64_t>(pts[k].x) - pts[k - 1].x)
                        + std::abs(static_cast<int64_t>(pts[k].y) - pts[k - 1].y);
                IPt prefer = (a.y == pts[i + 1].y) ? IPt{d.x, a.y} : IPt{a.x, d.y};
                IPt other = (a.y == pts[i + 1].y) ? IPt{a.x, d.y} : IPt{d.x, a.y};
                std::vector<IPt> best;
                int64_t best_len = old_len + 1;
                int best_n = 4;
                for (IPt elbow : {prefer, other}) {
                    std::vector<IPt> path;
                    path.push_back(a);
                    if (elbow.x != a.x || elbow.y != a.y)
                        path.push_back(elbow);
                    if (path.back().x != d.x || path.back().y != d.y)
                        path.push_back(d);
                    bool axes = path.size() >= 2;
                    for (std::size_t k = 1; k < path.size(); ++k)
                        axes = axes && ortho(path[k - 1], path[k]);
                    if (!axes || path.size() >= 4)
                        continue;
                    int64_t len = ortho_length(path);
                    if (len > old_len)
                        continue;
                    if (!best.empty() && (static_cast<int>(path.size()) > best_n || (static_cast<int>(path.size()) == best_n && len >= best_len)))
                        continue;
                    bool clear = true;
                    for (std::size_t k = 1; k < path.size() && clear; ++k) {
                        if (path[k].x == path[k - 1].x && path[k].y == path[k - 1].y)
                            continue;
                        if (jog_blocked(s, layer, net, margin, path[k - 1], path[k], ignore))
                            clear = false;
                    }
                    for (std::size_t k = 1; k < path.size() && clear; ++k) {
                        for (std::size_t m = 1; m < pts.size() && clear; ++m) {
                            if (m >= i + 1 && m <= j)
                                continue;
                            if (proper_cross(path[k - 1], path[k], pts[m - 1], pts[m])
                                || overlaps(path[k - 1], path[k], pts[m - 1], pts[m]))
                                clear = false;
                        }
                    }
                    if (!clear)
                        continue;
                    best = std::move(path);
                    best_len = len;
                    best_n = static_cast<int>(best.size());
                }
                if (best.empty())
                    continue;
                std::vector<IPt> next;
                next.insert(next.end(), pts.begin(), pts.begin() + static_cast<std::ptrdiff_t>(i));
                next.insert(next.end(), best.begin(), best.end());
                next.insert(next.end(), pts.begin() + static_cast<std::ptrdiff_t>(j + 1), pts.end());
                dedup_ortho(next);
                if (next.size() < 2 || next.size() >= pts.size() || next.front().x != pts.front().x || next.front().y != pts.front().y
                    || next.back().x != pts.back().x || next.back().y != pts.back().y)
                    continue;
                pts.swap(next);
                changed = true;
                spliced = true;
                break;
            }
            if (!spliced)
                ++i;
        }
    }
    return pts;
}

std::vector<IPt> pull_tight(const Snap& s, int layer, int net, int margin, const std::vector<IPt>& in, const std::vector<int>& ignore)
{
    std::vector<IPt> pts = in;
    auto drop_corners = [&]() {
        bool changed = true;
        while (changed && pts.size() >= 3) {
            changed = false;
            for (std::size_t i = 1; i + 1 < pts.size(); ++i) {
                if (is_anchor(s, pts[i]))
                    continue;
                if (!angle_ok(pts[i - 1], pts[i + 1], s.angle))
                    continue;
                if (!segment_hits(s, layer, pts[i - 1], pts[i + 1], net, margin, ignore)) {
                    pts.erase(pts.begin() + static_cast<std::ptrdiff_t>(i));
                    changed = true;
                    break;
                }
            }
        }
    };
    drop_corners();
    // any angle: slide the remaining corners until the legs touch the obstacles
    for (int round = 0; s.angle == 2 && round < 16 && pts.size() >= 3; ++round) {
        bool moved = false;
        for (std::size_t i = 1; i + 1 < pts.size(); ++i) {
            if (is_anchor(s, pts[i]))
                continue;
            const IPt p0 = pts[i - 1];
            const IPt p2 = pts[i + 1];
            auto len = [](IPt a, IPt b) { return std::hypot(static_cast<double>(b.x) - a.x, static_cast<double>(b.y) - a.y); };
            // the board rounds oblique trace shapes outwards
            const int slack = margin + 2;
            auto legs_clear = [&](IPt n, bool leg0, bool leg2) {
                if (leg0 && !(n.x == p0.x && n.y == p0.y) && segment_hits(s, layer, p0, n, net, slack, ignore))
                    return false;
                if (leg2 && !(n.x == p2.x && n.y == p2.y) && segment_hits(s, layer, n, p2, net, slack, ignore))
                    return false;
                return true;
            };
            auto slide = [&](IPt from, double tx, double ty, bool leg0, bool leg2) {
                auto at = [&](double t) {
                    return IPt{static_cast<int32_t>(std::lround(from.x + t * (tx - from.x))),
                        static_cast<int32_t>(std::lround(from.y + t * (ty - from.y)))};
                };
                if (legs_clear(at(1.0), leg0, leg2))
                    return at(1.0);
                double lo = 0.0;
                double hi = 1.0;
                for (int k = 0; k < 14; ++k) {
                    double mid = 0.5 * (lo + hi);
                    if (legs_clear(at(mid), leg0, leg2))
                        lo = mid;
                    else
                        hi = mid;
                }
                return at(lo);
            };
            IPt p1 = pts[i];
            const double before = len(p0, p1) + len(p1, p2);
            double cx = p2.x - p0.x;
            double cy = p2.y - p0.y;
            double cc = cx * cx + cy * cy;
            double t = cc > 0 ? std::clamp(((p1.x - p0.x) * cx + (p1.y - p0.y) * cy) / cc, 0.0, 1.0) : 0.0;
            IPt best = p1;
            double best_len = before;
            for (IPt n : {slide(p1, p0.x, p0.y, false, true), slide(p1, p2.x, p2.y, true, false),
                     slide(p1, p0.x + t * cx, p0.y + t * cy, true, true)}) {
                double l = len(p0, n) + len(n, p2);
                if (l < best_len - 0.5 && !is_anchor(s, n)) {
                    best = n;
                    best_len = l;
                }
            }
            if (best.x != p1.x || best.y != p1.y) {
                pts[i] = best;
                moved = true;
            }
        }
        pts.erase(std::unique(pts.begin(), pts.end(), [](IPt a, IPt b) { return a.x == b.x && a.y == b.y; }), pts.end());
        drop_corners();
        if (!moved)
            break;
    }
    std::vector<IPt> slim;
    for (const IPt& p : pts) {
        if (slim.size() >= 2) {
            IPt a = slim[slim.size() - 2];
            IPt b = slim.back();
            if ((a.x == b.x && b.x == p.x) || (a.y == b.y && b.y == p.y))
                slim.back() = p;
            else
                slim.push_back(p);
        } else
            slim.push_back(p);
    }
    return slim;
}

bool via_point_blocked(const Snap& s, IPt p, int net, const std::vector<IPt>& extra, bool* reuse)
{
    *reuse = false;
    if (!via_fits(s, p.x, p.y))
        return true;
    int sep = std::max(1, 2 * s.via_r + pair_clearance(s, s.via_clearance, s.via_clearance, 0));
    // board clearance uses bounding octagons of the circles, plus rounding
    const int64_t sep_axis = sep + 2;
    const int64_t sep_diag = static_cast<int64_t>(std::ceil(sep * std::sqrt(2.0))) + 24;
    // with 90 degree rules the board search tree holds boxes, so the octagon cut does not apply
    const bool boxes = s.angle == 0;
    auto crowded = [&](int32_t x, int32_t y) {
        int64_t dx = std::abs(static_cast<int64_t>(p.x) - x);
        int64_t dy = std::abs(static_cast<int64_t>(p.y) - y);
        return std::max(dx, dy) < sep_axis && (boxes || dx + dy < sep_diag);
    };
    auto seg_in_square = [&](IPt c, IPt d, int64_t h) {
        double t0 = 0.0;
        double t1 = 1.0;
        const double dx = static_cast<double>(d.x) - c.x;
        const double dy = static_cast<double>(d.y) - c.y;
        const double lo[2] = {static_cast<double>(p.x - h) - c.x, static_cast<double>(p.y - h) - c.y};
        const double hi[2] = {static_cast<double>(p.x + h) - c.x, static_cast<double>(p.y + h) - c.y};
        const double dir[2] = {dx, dy};
        for (int k = 0; k < 2; ++k) {
            if (dir[k] == 0.0) {
                if (lo[k] >= 0.0 || hi[k] <= 0.0)
                    return false;
                continue;
            }
            double a = lo[k] / dir[k];
            double b = hi[k] / dir[k];
            if (a > b)
                std::swap(a, b);
            t0 = std::max(t0, a);
            t1 = std::min(t1, b);
            if (t0 > t1)
                return false;
        }
        return true;
    };
    for (const SnapItem& it : s.items) {
        if (it.kind == Kind::Via) {
            if (p.x == it.center.x && p.y == it.center.y && it.net == net) {
                *reuse = true;
                continue;
            }
            if (crowded(it.center.x, it.center.y))
                return true;
        } else if (it.kind == Kind::Trace) {
            if (it.net == net || it.corners.size() < 2)
                continue;
            // the via counts as its bounding octagon (circumradius r / cos 22.5°)
            int oct_r = (boxes ? s.via_r : static_cast<int>(std::ceil(s.via_r * 1.0824))) + 2;
            int need = oct_r + item_half_width(s, it.net, it.layer0) + pair_clearance(s, s.via_clearance, it.clearance, it.layer0);
            double lim = static_cast<double>(need) * static_cast<double>(need);
            int32_t x0 = p.x - need;
            int32_t x1 = p.x + need;
            int32_t y0 = p.y - need;
            int32_t y1 = p.y + need;
            for (std::size_t k = 1; k < it.corners.size(); ++k) {
                const IPt& c = it.corners[k - 1];
                const IPt& d = it.corners[k];
                if (std::max(c.x, d.x) < x0 || std::min(c.x, d.x) > x1 || std::max(c.y, d.y) < y0 || std::min(c.y, d.y) > y1)
                    continue;
                if (boxes ? seg_in_square(c, d, need) : dist2_seg(c, d, p.x, p.y) < lim)
                    return true;
            }
        } else if (it.kind == Kind::Pin || it.kind == Kind::Keepout || it.kind == Kind::ViaKeepout) {
            int pad = s.via_r + pair_clearance(s, s.via_clearance, it.clearance, it.layer0);
            if (touches_pt(it.box, p.x, p.y, pad))
                return true;
        }
    }
    for (const IPt& e : extra) {
        if (crowded(e.x, e.y))
            return true;
    }
    return false;
}

// geometry::planar::Polygon drops repeated and collinear corners; fewer than 2 left gives no trace
bool polyline_degenerate(const std::vector<IPt>& path)
{
    std::vector<IPt> rest;
    for (const IPt& p : path) {
        if (!rest.empty() && rest.back().x == p.x && rest.back().y == p.y)
            continue;
        while (rest.size() >= 2) {
            const IPt& a = rest[rest.size() - 2];
            const IPt& b = rest.back();
            int64_t cross = static_cast<int64_t>(b.x - a.x) * (p.y - a.y) - static_cast<int64_t>(b.y - a.y) * (p.x - a.x);
            if (cross != 0)
                break;
            rest.pop_back();
        }
        if (!rest.empty() && rest.back().x == p.x && rest.back().y == p.y)
            continue;
        rest.push_back(p);
    }
    return rest.size() < 2;
}

// shove: like InsertFoundConnectionAlgo, push the ripped items aside instead of requiring them removed
bool commit_path(Snap& s, Found& found, int net, int half_w, const std::vector<char>& own, bool shove = false)
{
    if (!found.ok)
        return false;
    std::vector<int> ignore;
    for (int rip : found.rip_items)
        ignore.push_back(rip);
    const int use_w = half_w;
    std::vector<IPt> pts = found.pts;
    if (pts.size() < 2 && !found.has_via)
        return false;
    for (int rip : found.rip_items) {
        if (shove || rip < 0 || rip >= static_cast<int>(s.items.size()))
            continue;
        const SnapItem& it = s.items[static_cast<std::size_t>(rip)];
        if (it.item == nullptr || it.fixed)
            continue;
        return false;
    }
    if (found.pt_layer.size() != found.pts.size())
        found.pt_layer.assign(found.pts.size(), found.layer);
    std::vector<IPt> via_pts;
    for (std::size_t i = 1; i < found.pts.size(); ++i) {
        if (found.pt_layer[i] != found.pt_layer[i - 1])
            via_pts.push_back(found.pts[i]);
    }
    if (via_pts.empty() && found.has_via && found.pts.size() < 2)
        via_pts.push_back(IPt{found.via_x, found.via_y});
    std::vector<char> place_via(via_pts.size(), 1);
    std::vector<IPt> planned;
    if (s.vias_allowed && s.via_pad != nullptr) {
        for (std::size_t i = 0; i < via_pts.size(); ++i) {
            bool reuse = false;
            if (via_point_blocked(s, via_pts[i], net, planned, &reuse) && !shove)
                return false;
            if (reuse)
                place_via[i] = 0;
            else
                planned.push_back(via_pts[i]);
        }
    }
    std::size_t via_i = 0;
    int cl = 1;
    for (std::size_t i = 0; i < s.items.size() && i < own.size(); ++i) {
        if (own[i]) {
            cl = s.items[i].clearance;
            break;
        }
    }
    struct Run {
        std::vector<IPt> pts;
        int layer = 0;
        bool place_via = false;
        IPt via;
    };
    std::vector<Run> runs;
    std::vector<IPt> run;
    int run_layer = found.pts.empty() ? found.layer : found.pt_layer[0];
    for (std::size_t i = 0; i < found.pts.size(); ++i) {
        int layer = found.pt_layer[i];
        if (!run.empty() && layer != run_layer) {
            run.push_back(found.pts[i]);
            Run piece;
            piece.pts = run;
            piece.layer = run_layer;
            if (via_i < via_pts.size()) {
                piece.via = via_pts[via_i];
                piece.place_via = via_i < place_via.size() && place_via[via_i] != 0;
                ++via_i;
            }
            runs.push_back(std::move(piece));
            run.clear();
            run.push_back(found.pts[i]);
            run_layer = layer;
        } else
            run.push_back(found.pts[i]);
    }
    if (run.size() >= 2) {
        Run piece;
        piece.pts = std::move(run);
        piece.layer = run_layer;
        runs.push_back(std::move(piece));
    }
    auto hits = [&](const std::vector<IPt>& path, int layer) {
        for (std::size_t k = 1; k < path.size(); ++k) {
            IPt a = path[k - 1];
            IPt b = path[k];
            int steps = std::max(std::abs(a.x - b.x), std::abs(a.y - b.y));
            steps = std::max(1, steps / std::max(1, use_w));
            if (steps > 64)
                steps = 64;
            for (int step = 0; step <= steps; ++step) {
                int32_t x = a.x + static_cast<int32_t>((static_cast<int64_t>(b.x - a.x) * step) / steps);
                int32_t y = a.y + static_cast<int32_t>((static_cast<int64_t>(b.y - a.y) * step) / steps);
                if (!inside_board(s, x, y))
                    return true;
                for (const SnapItem& it : s.items) {
                    if (it.kind != Kind::Keepout || !on_layer(it, layer))
                        continue;
                    int pad = use_w + pair_clearance(s, 1, it.clearance, layer);
                    if (x > it.box.x0 - pad && x < it.box.x1 + pad && y > it.box.y0 - pad && y < it.box.y1 + pad)
                        return true;
                }
            }
        }
        return false;
    };
    auto bend = [&](const std::vector<IPt>& in, int layer) -> std::vector<IPt> {
        std::vector<IPt> pts;
        if (in.empty())
            return pts;
        append_unique(pts, in.front());
        for (std::size_t i = 1; i < in.size(); ++i) {
            IPt a = pts.back();
            IPt b = in[i];
            if (a.x == b.x || a.y == b.y) {
                if (hits(std::vector<IPt>{a, b}, layer))
                    return {};
                if ((a.x != b.x || a.y != b.y) && segment_hits(s, layer, a, b, net, use_w, ignore))
                    return {};
                append_unique(pts, b);
                continue;
            }
            auto clear_poly = [&](const std::vector<IPt>& poly) {
                for (std::size_t k = 1; k < poly.size(); ++k) {
                    if (hits(std::vector<IPt>{poly[k - 1], poly[k]}, layer))
                        return false;
                    if (segment_hits(s, layer, poly[k - 1], poly[k], net, use_w, ignore))
                        return false;
                }
                return poly.size() >= 2;
            };
            std::vector<IPt> chosen;
            if (s.angle >= 2 && clear_poly({a, b}))
                chosen = {a, b};
            if (chosen.empty()) {
                IPt e1{b.x, a.y};
                IPt e2{a.x, b.y};
                if (clear_poly({a, e1, b}))
                    chosen = {a, e1, b};
                else if (clear_poly({a, e2, b}))
                    chosen = {a, e2, b};
                else {
                    for (int k = 1; k <= 7 && chosen.empty(); ++k) {
                        int32_t x = a.x + static_cast<int32_t>((static_cast<int64_t>(b.x - a.x) * k) / 8);
                        int32_t y = a.y + static_cast<int32_t>((static_cast<int64_t>(b.y - a.y) * k) / 8);
                        IPt p{x, a.y};
                        IPt q{x, b.y};
                        if (clear_poly({a, p, q, b}))
                            chosen = {a, p, q, b};
                        else {
                            IPt r{a.x, y};
                            IPt t{b.x, y};
                            if (clear_poly({a, r, t, b}))
                                chosen = {a, r, t, b};
                        }
                    }
                }
            }
            if (chosen.empty())
                return {};
            for (std::size_t k = 1; k < chosen.size(); ++k)
                append_unique(pts, chosen[k]);
        }
        return pts;
    };
    for (Run& piece : runs) {
        std::vector<IPt> shaped = bend(piece.pts, piece.layer);
        if (shaped.size() < 2)
            return false;
        std::vector<IPt> tight = pull_tight(s, piece.layer, net, use_w, shaped, ignore);
        if (tight.size() >= 2 && !hits(tight, piece.layer) && path_clear(s, piece.layer, net, use_w, tight, ignore))
            shaped = std::move(tight);
        piece.pts = std::move(shaped);
    }
    java::Array<int32_t> nets(1);
    nets[0] = net;
    rules::ViaRule* rule = s.board->rules->get_default_via_rule();
    rules::ViaInfo* via_info = rule != nullptr && rule->via_count() > 0 ? rule->get_via(0) : nullptr;
    // AutorouteControl defaults of the batch autorouter
    const int max_trace_depth = 20;
    const int max_via_depth = 5;
    const int max_spring_depth = 5;
    const int accuracy = 500;
    java::Array<int32_t> half_arr(s.layers);
    for (int i = 0; i < s.layers; ++i)
        half_arr[i] = use_w;
    auto insert_run = [&](const Run& piece) {
        if (polyline_degenerate(piece.pts))
            return true;
        java::Array<geometry::planar::Point*> arr(static_cast<int32_t>(piece.pts.size()));
        for (std::size_t i = 0; i < piece.pts.size(); ++i)
            arr[static_cast<int32_t>(i)] = new geometry::planar::IntPoint(piece.pts[i].x, piece.pts[i].y);
        geometry::planar::Polyline* poly = new geometry::planar::Polyline(arr);
        if (!shove) {
            s.board->insert_trace_without_cleaning(poly, piece.layer, use_w, nets, cl, board::FixedState::UNFIXED);
            return true;
        }
        geometry::planar::Point* ok = s.board->insert_forced_trace_polyline(poly, use_w, piece.layer, nets, cl,
            max_trace_depth, max_via_depth, max_spring_depth, std::numeric_limits<int32_t>::max(), accuracy, true, nullptr);
        bool done = ok != nullptr && ok->equals(poly->last_corner());
        if (s.board->item_list->track_dropped)
            s.board->retired_polylines.push_back(poly);
        return done;
    };
    auto insert_via = [&](IPt at) {
        geometry::planar::IntPoint* via_at = new geometry::planar::IntPoint(at.x, at.y);
        if (!shove) {
            s.board->insert_via(s.via_pad, via_at, nets, s.via_clearance, board::FixedState::UNFIXED, true);
            return true;
        }
        for (const SnapItem& it : s.items) {
            if (it.kind == Kind::Via && it.net == net && it.center.x == at.x && it.center.y == at.y)
                return true;
        }
        return via_info != nullptr
            && board::ForcedViaAlgo::check(via_info, via_at, nets, max_trace_depth, max_via_depth, s.board)
            && board::ForcedViaAlgo::insert(via_info, via_at, nets, cl, half_arr, max_trace_depth, max_via_depth, s.board);
    };
    for (const Run& piece : runs) {
        if (!insert_run(piece))
            return false;
        if (piece.place_via && s.via_pad != nullptr && s.vias_allowed && !insert_via(piece.via))
            return false;
    }
    if (runs.empty() && found.has_via && s.via_pad != nullptr && (place_via.empty() || place_via[0] != 0))
        return insert_via(IPt{found.via_x, found.via_y});
    return !runs.empty();
}

bool shove_commit(Snap& s, Found found, int net, int half_w, const std::vector<char>& start, const std::vector<char>& dest)
{
    board::Item* from_item = nullptr;
    board::Item* to_item = nullptr;
    for (std::size_t i = 0; i < s.items.size(); ++i) {
        if (i < start.size() && start[i] && from_item == nullptr)
            from_item = s.items[i].item;
        if (i < dest.size() && dest[i] && to_item == nullptr)
            to_item = s.items[i].item;
    }
    if (from_item == nullptr || to_item == nullptr)
        return false;
    std::unordered_set<board::Item*> before;
    for (const SnapItem& it : s.items)
        before.insert(it.item);
    if (!commit_path(s, found, net, half_w, start, true))
        return false;
    java::util::TreeSet<board::Item*>* joined = from_item->get_connected_set(net);
    const bool connected = joined != nullptr && joined->contains(to_item);
    delete joined;
    if (!connected)
        return false;
    // shoved and new items must keep their clearance
    bool clean = true;
    auto* items = s.board->get_items();
    auto* it = items != nullptr ? items->iterator() : nullptr;
    while (clean && it != nullptr && it->hasNext()) {
        board::Item* item = it->next();
        if (item == nullptr || before.count(item) != 0)
            continue;
        auto* violations = item->clearance_violations();
        clean = violations == nullptr || violations->size() == 0;
        delete violations;
    }
    delete it;
    delete items;
    return clean;
}

// BatchAutorouter: ripping costs start_ripup_costs * pass * trace half width / detour, once per item
void set_rip_costs(Snap& snap)
{
    snap.rip_cost.assign(snap.items.size(), 0.0);
    for (std::size_t i = 0; i < snap.items.size(); ++i) {
        const SnapItem& it = snap.items[i];
        if (it.kind != Kind::Trace || it.corners.size() < 2)
            continue;
        double len = 0;
        for (std::size_t k = 1; k < it.corners.size(); ++k)
            len += std::hypot(static_cast<double>(it.corners[k].x) - it.corners[k - 1].x,
                static_cast<double>(it.corners[k].y) - it.corners[k - 1].y);
        const IPt& a = it.corners.front();
        const IPt& b = it.corners.back();
        double air = std::hypot(static_cast<double>(b.x) - a.x, static_cast<double>(b.y) - a.y);
        double detour = air > 0 ? std::max(1.0, len / air) : 1.0;
        snap.rip_cost[i] = std::max(1.0, snap.ripup_cost * trace_half(snap, it) / detour);
    }
}

bool route_pair(Snap& snap, Maze& maze, interactive::Settings* settings, int via_costs, int pass_no,
    bool fanout, int net, const std::vector<char>& is_start, const std::vector<char>& is_dest,
    const std::function<bool()>& stop, double max_ms, std::vector<int>* ripped_nets = nullptr)
{
    const bool allow_rip = ripped_nets != nullptr && !fanout;
    (void)pass_no;
    if (via_costs > 0)
        snap.via_cost = via_costs * std::max(1, snap.via_r);
    if (net > 0) {
        rules::Net* route_net = snap.board->rules->nets->get(net);
        if (route_net != nullptr && route_net->contains_plane() && settings != nullptr)
            snap.via_cost = settings->autoroute_settings->get_plane_via_costs() * std::max(1, snap.via_r);
        snap.half_w = item_half_width(snap, net, 0);
    }
    IPt a{0, 0};
    IPt b{0, 0};
    bool have_a = false;
    bool have_b = false;
    for (std::size_t i = 0; i < snap.items.size(); ++i) {
        if (is_start.size() == snap.items.size() && is_start[i] && !have_a) {
            a = snap.items[i].center;
            have_a = true;
        }
        if (is_dest.size() == snap.items.size() && is_dest[i] && !have_b) {
            b = snap.items[i].center;
            have_b = true;
        }
    }
    refresh_angle(snap);
    if (have_a && have_b)
        set_airline(true, a.x, a.y, b.x, b.y);
    note_paint();
    int layer_a = 0;
    int layer_a1 = 0;
    int layer_b = 0;
    int layer_b1 = 0;
    for (std::size_t i = 0; i < snap.items.size(); ++i) {
        if (is_start.size() == snap.items.size() && is_start[i]) {
            layer_a = snap.items[i].layer0;
            layer_a1 = snap.items[i].layer1;
            break;
        }
    }
    for (std::size_t i = 0; i < snap.items.size(); ++i) {
        if (is_dest.size() == snap.items.size() && is_dest[i]) {
            layer_b = snap.items[i].layer0;
            layer_b1 = snap.items[i].layer1;
            break;
        }
    }
    bool layer_a_on = layer_a >= 0 && layer_a < static_cast<int>(snap.layer_on.size())
        && snap.layer_on[static_cast<std::size_t>(layer_a)] != 0;
    if (have_a && have_b && !fanout && layer_a == layer_b && layer_a_on) {
        std::vector<std::vector<IPt>> candidates;
        if (snap.angle == 1 && a.x != b.x && a.y != b.y) {
            const int32_t dx = b.x - a.x;
            const int32_t dy = b.y - a.y;
            const int32_t d = std::min(std::abs(dx), std::abs(dy));
            const IPt diag{a.x + (dx < 0 ? -d : d), a.y + (dy < 0 ? -d : d)};
            const IPt diag_end{b.x - (dx < 0 ? -d : d), b.y - (dy < 0 ? -d : d)};
            std::vector<IPt> first{a};
            append_unique(first, diag);
            append_unique(first, b);
            candidates.push_back(first);
            std::vector<IPt> last{a};
            append_unique(last, diag_end);
            append_unique(last, b);
            candidates.push_back(last);
        }
        candidates.push_back(orthogonalize({a, b}, snap.angle == 1 ? 0 : snap.angle));
        std::vector<int> none;
        for (const std::vector<IPt>& direct : candidates) {
            bool clear = direct.size() >= 2;
            for (std::size_t i = 1; i < direct.size() && clear; ++i) {
                // the board rounds oblique trace shapes outwards
                const bool oblique = direct[i - 1].x != direct[i].x && direct[i - 1].y != direct[i].y;
                if (segment_hits(snap, layer_a, direct[i - 1], direct[i], net, snap.half_w + (oblique ? 2 : 0), none))
                    clear = false;
            }
            if (!clear)
                continue;
            Found straight;
            straight.ok = true;
            straight.pts = direct;
            straight.pt_layer.assign(direct.size(), layer_a);
            straight.layer = layer_a;
            std::vector<char> own = is_start;
            if (commit_path(snap, straight, net, snap.half_w, own)) {
                set_airline(false, 0, 0, 0, 0);
                return true;
            }
        }
    }
    auto deadline = std::chrono::steady_clock::now() + std::chrono::milliseconds(static_cast<int>(std::min(max_ms, static_cast<double>(std::numeric_limits<int>::max()))));
    bool routed = false;
    std::vector<char> start(snap.items.size(), 0);
    std::vector<char> dest(snap.items.size(), 0);
    if (is_start.size() == snap.items.size())
        start = is_start;
    if (is_dest.size() == snap.items.size())
        dest = is_dest;
    std::vector<char> none(snap.items.size(), 0);
    do {
        const int half_w = snap.half_w;
        Maze& active = maze;
        const bool rip_now = allow_rip;
        bool reuse = active.built_gen == snap.generation && active.built_half_w == half_w && active.built_rip == rip_now
            && (!rip_now || active.built_net == net) && !active.rooms.empty();
        if (reuse)
            active.clear_wave();
        else {
            active.reset();
            for (int layer = 0; layer < snap.layers; ++layer) {
                if (layer < static_cast<int>(snap.layer_on.size()) && !snap.layer_on[static_cast<std::size_t>(layer)])
                    continue;
                std::vector<int> unused;
                build_rooms(snap, net, layer, half_w, rip_now, none, none, active, unused, true);
                link_doors(active, layer, half_w);
            }
            build_drills(snap, active, net);
            active.built_gen = snap.generation;
            active.built_half_w = half_w;
            active.built_rip = rip_now;
            active.built_net = net;
        }
        for (int layer = 0; layer < snap.layers; ++layer) {
            if (layer < static_cast<int>(snap.layer_on.size()) && !snap.layer_on[static_cast<std::size_t>(layer)])
                continue;
            mark_terminals(snap, active, layer, start, false);
            mark_terminals(snap, active, layer, dest, true);
        }
        bool any_start = false;
        bool any_dest = false;
        for (const Room& room : active.rooms) {
            any_start = any_start || room.start;
            any_dest = any_dest || room.dest;
        }
        if (!java::fr_eq(snap.board->get_test_level(), board::TestLevel::RELEASE_VERSION))
            std::cerr << "autoroute2 rooms " << active.rooms.size()
                      << " doors " << active.doors.size() << " start " << any_start << " dest " << any_dest << "\n";
        if (!any_start || (!any_dest && !fanout))
            continue;
        snap.fanout = fanout;
        if (rip_now) {
            set_rip_costs(snap);
        }
        Found found = search_wave(snap, active, net, half_w, deadline, stop);
        snap.rip_cost.clear();
        if (found.ok && !fanout) {
            if (found.pt_layer.size() != found.pts.size())
                found.pt_layer.assign(found.pts.size(), found.layer);
            if (found.has_start && !found.pt_layer.empty()) {
                int leave = found.pt_layer.front();
                found.pts.insert(found.pts.begin(), found.start_entry);
                found.pt_layer.insert(found.pt_layer.begin(), leave);
                found.pts.insert(found.pts.begin(), found.start_at);
                found.pt_layer.insert(found.pt_layer.begin(), leave);
            } else if (have_a) {
                int leave = found.pt_layer.empty() ? layer_a : found.pt_layer.front();
                int use = leave >= layer_a && leave <= layer_a1 ? leave : layer_a;
                found.pts.insert(found.pts.begin(), a);
                found.pt_layer.insert(found.pt_layer.begin(), use);
            }
            if (found.has_goal && !found.pt_layer.empty()) {
                int arrive = found.pt_layer.back();
                found.pts.push_back(found.goal_entry);
                found.pt_layer.push_back(arrive);
                found.pts.push_back(found.goal);
                found.pt_layer.push_back(arrive);
            } else if (have_b) {
                int arrive = found.pt_layer.empty() ? layer_b : found.pt_layer.back();
                int use = arrive >= layer_b && arrive <= layer_b1 ? arrive : layer_b;
                found.pts.push_back(b);
                found.pt_layer.push_back(use);
            }
            found.ok = found.pts.size() >= 2 || found.has_via;
        }
        if (!java::fr_eq(snap.board->get_test_level(), board::TestLevel::RELEASE_VERSION))
            std::cerr << "autoroute2 wave " << found.ok << " pts " << found.pts.size() << "\n";
        const int keep_via_cost = snap.via_cost;
        const int keep_half = snap.half_w;
        // undo restores clones of the changed items, so the snapshot has to be read again
        auto reread = [&]() {
            read_snapshot(snap, snap.board, settings, via_costs, pass_no, false);
            snap.via_cost = keep_via_cost;
            snap.half_w = keep_half;
        };
        bool shoved = false;
        if (found.ok && !found.rip_items.empty()) {
            // reread renumbers the snapshot, so the marks survive the undo by item id
            auto id_at = [&](std::size_t i) {
                return i < snap.items.size() && snap.items[i].item != nullptr ? snap.items[i].item->get_id_no() : -1;
            };
            std::vector<int> rip_ids;
            std::vector<int> start_ids;
            std::vector<int> dest_ids;
            for (int id : found.rip_items)
                rip_ids.push_back(id >= 0 ? id_at(static_cast<std::size_t>(id)) : -1);
            for (std::size_t i = 0; i < snap.items.size(); ++i) {
                if (i < start.size() && start[i])
                    start_ids.push_back(id_at(i));
                if (i < dest.size() && dest[i])
                    dest_ids.push_back(id_at(i));
            }
            snap.board->generate_snapshot();
            shoved = shove_commit(snap, found, net, half_w, start, dest);
            if (shoved) {
                snap.board->pop_snapshot();
                if (snap.board->components != nullptr && snap.board->components->undo_list != nullptr)
                    snap.board->components->undo_list->pop_snapshot();
                routed = true;
            } else {
                snap.board->undo(nullptr);
                reread();
                std::unordered_map<int, int> index;
                for (std::size_t i = 0; i < snap.items.size(); ++i)
                    index[id_at(i)] = static_cast<int>(i);
                auto remap = [&](const std::vector<int>& ids, std::vector<char>& mark) {
                    mark.assign(snap.items.size(), 0);
                    for (int id : ids) {
                        auto hit = index.find(id);
                        if (id >= 0 && hit != index.end())
                            mark[static_cast<std::size_t>(hit->second)] = 1;
                    }
                };
                remap(start_ids, start);
                remap(dest_ids, dest);
                found.rip_items.clear();
                for (int id : rip_ids) {
                    auto hit = index.find(id);
                    found.rip_items.push_back(id >= 0 && hit != index.end() ? hit->second : -1);
                }
            }
            if (!java::fr_eq(snap.board->get_test_level(), board::TestLevel::RELEASE_VERSION))
                std::cerr << "autoroute2 shove " << shoved << "\n";
        }
        if (!shoved && found.ok && !found.rip_items.empty()) {
            // AutorouteEngine: remove the connections of the ripped items, then insert the new route
            std::vector<board::Item*> doomed;
            std::set<board::Item*> seen;
            bool blocked = false;
            for (int id : found.rip_items) {
                if (id < 0 || id >= static_cast<int>(snap.items.size())) {
                    blocked = true;
                    continue;
                }
                const SnapItem& it = snap.items[static_cast<std::size_t>(id)];
                if (it.item == nullptr || it.fixed || it.net == net) {
                    blocked = true;
                    continue;
                }
                java::util::TreeSet<board::Item*>* conn = it.item->get_connection_items(board::Item_StopConnectionOption::NONE);
                if (conn != nullptr) {
                    for (auto* member : java::iterate(conn)) {
                        board::Item* m = java::narrow<board::Item*>(member);
                        if (m == nullptr || !m->is_route() || !seen.insert(m).second)
                            continue;
                        blocked = blocked || m->is_user_fixed();
                        doomed.push_back(m);
                    }
                    delete conn;
                }
                if (seen.insert(it.item).second)
                    doomed.push_back(it.item);
            }
            if (blocked || doomed.empty()) {
                found.ok = false;
            } else {
                std::set<board::Item*> own_items;
                for (std::size_t i = 0; i < snap.items.size() && i < start.size(); ++i) {
                    if (start[i] && snap.items[i].item != nullptr)
                        own_items.insert(snap.items[i].item);
                }
                std::vector<int> hit_nets;
                for (board::Item* d : doomed) {
                    if (d->net_count() > 0 && std::find(hit_nets.begin(), hit_nets.end(), d->get_net_no(0)) == hit_nets.end())
                        hit_nets.push_back(d->get_net_no(0));
                }
                snap.board->generate_snapshot();
                for (board::Item* d : doomed)
                    snap.board->remove_item(d);
                reread();
                std::vector<char> own(snap.items.size(), 0);
                for (std::size_t i = 0; i < snap.items.size(); ++i)
                    own[i] = own_items.count(snap.items[i].item) != 0 ? 1 : 0;
                found.rip_items.clear();
                routed = commit_path(snap, found, net, half_w, own);
                if (!java::fr_eq(snap.board->get_test_level(), board::TestLevel::RELEASE_VERSION))
                    std::cerr << "autoroute2 rip " << doomed.size() << " nets " << hit_nets.size() << " commit " << routed << "\n";
                if (routed) {
                    snap.board->pop_snapshot();
                    if (snap.board->components != nullptr && snap.board->components->undo_list != nullptr)
                        snap.board->components->undo_list->pop_snapshot();
                    ripped_nets->insert(ripped_nets->end(), hit_nets.begin(), hit_nets.end());
                } else {
                    snap.board->undo(nullptr);
                    reread();
                }
            }
        } else if (found.ok && !shoved) {
            routed = commit_path(snap, found, net, half_w, start);
        }
    } while (false);
    set_airline(false, 0, 0, 0, 0);
    return routed;
}

bool pins_have_rooms(board::RoutingBoard* board, interactive::Settings* settings)
{
    Snap snap;
    read_snapshot(snap, board, settings, 1, 1, false);
    Maze maze;
    std::vector<char> none(snap.items.size(), 0);
    std::vector<char> pins(snap.items.size(), 0);
    int pin_count = 0;
    for (std::size_t i = 0; i < snap.items.size(); ++i) {
        if (snap.items[i].kind == Kind::Pin) {
            pins[i] = 1;
            ++pin_count;
        }
    }
    if (pin_count == 0)
        return true;
    std::vector<int> unused;
    build_rooms(snap, -1, 0, snap.half_w, false, none, pins, maze, unused, false);
    int touched = 0;
    for (const Room& room : maze.rooms) {
        if (room.dest)
            ++touched;
    }
    maze.reset();
    return touched > 0;
}

struct OpenNet {
    int net = 0;
    int comp_a = -1;
    int comp_b = -1;
    bool plane = false;
};

std::vector<OpenNet> open_nets(const Snap& snap)
{
    struct Comp {
        int net = 0;
        int id = -1;
        bool plane = false;
        int pins = 0;
    };
    std::vector<Comp> comps;
    std::unordered_map<uint64_t, std::size_t> index;
    index.reserve(snap.items.size());
    for (const SnapItem& it : snap.items) {
        if (it.component < 0 || it.net <= 0)
            continue;
        if (it.kind != Kind::Pin && it.kind != Kind::Via && it.kind != Kind::Trace && it.kind != Kind::Plane)
            continue;
        uint64_t key = (static_cast<uint64_t>(static_cast<uint32_t>(it.net)) << 32) | static_cast<uint32_t>(it.component);
        auto known = index.find(key);
        if (known == index.end()) {
            index.emplace(key, comps.size());
            comps.push_back(Comp{it.net, it.component, it.kind == Kind::Plane, it.kind == Kind::Pin ? 1 : 0});
        } else {
            if (it.kind == Kind::Plane)
                comps[known->second].plane = true;
            if (it.kind == Kind::Pin)
                ++comps[known->second].pins;
        }
    }
    std::unordered_map<int, std::vector<int>> by_net;
    std::vector<int> order;
    for (std::size_t i = 0; i < comps.size(); ++i) {
        int net = comps[i].net;
        if (by_net.find(net) == by_net.end())
            order.push_back(net);
        by_net[net].push_back(static_cast<int>(i));
    }
    std::vector<OpenNet> open;
    open.reserve(order.size());
    for (int net : order) {
        const std::vector<int>& group = by_net[net];
        int small = group[0];
        int large = -1;
        bool pin_group = false;
        for (int idx : group)
            pin_group = pin_group || comps[static_cast<std::size_t>(idx)].pins > 0;
        if (pin_group) {
            small = -1;
            for (int idx : group) {
                if (comps[static_cast<std::size_t>(idx)].pins <= 0)
                    continue;
                if (small < 0 || comps[static_cast<std::size_t>(idx)].pins < comps[static_cast<std::size_t>(small)].pins)
                    small = idx;
            }
            for (int idx : group) {
                if (idx == small || comps[static_cast<std::size_t>(idx)].pins <= 0)
                    continue;
                if (large < 0 || comps[static_cast<std::size_t>(idx)].pins > comps[static_cast<std::size_t>(large)].pins)
                    large = idx;
            }
        }
        if (large < 0) {
            for (int idx : group) {
                if (idx != small) {
                    large = idx;
                    break;
                }
            }
        }
        if (small < 0 || large < 0)
            continue;
        const Comp& ca = comps[static_cast<std::size_t>(small)];
        const Comp& cb = comps[static_cast<std::size_t>(large)];
        OpenNet row;
        row.net = net;
        row.plane = ca.plane || cb.plane;
        if (ca.plane && !cb.plane) {
            row.comp_a = cb.id;
            row.comp_b = ca.id;
        } else {
            row.comp_a = ca.id;
            row.comp_b = cb.id;
        }
        open.push_back(row);
    }
    return open;
}

void flags_for(const Snap& snap, int net, int comp, std::vector<char>& flags)
{
    flags.assign(snap.items.size(), 0);
    for (std::size_t i = 0; i < snap.items.size(); ++i) {
        if (snap.items[i].net == net && snap.items[i].component == comp)
            flags[i] = 1;
    }
}

void show_autoroute_result(interactive::BoardHandling* hdlg, int passes, int routed, int failed)
{
    if (hdlg == nullptr || hdlg->screen_messages == nullptr)
        return;
    java::util::ResourceBundle resources = java::util::ResourceBundle::getBundle(QString::fromUtf8("\x69\x6e\x74\x65\x72\x61\x63\x74\x69\x76\x65\x2e\x72\x65\x73\x6f\x75\x72\x63\x65\x73\x2e\x49\x6e\x74\x65\x72\x61\x63\x74\x69\x76\x65\x53\x74\x61\x74\x65", 38), hdlg->get_locale());
    QString pattern = resources.getString(QString::fromUtf8("autoroute_result"));
    hdlg->screen_messages->set_status_message(pattern.arg(passes).arg(routed).arg(failed));
    hdlg->screen_messages->set_batch_autoroute_info(failed, routed, 0, failed);
}

void show_postroute(interactive::BoardHandling* hdlg, bool finished, bool stopped, bool keep_status = false)
{
    if (hdlg == nullptr || hdlg->screen_messages == nullptr)
        return;
    java::util::ResourceBundle resources = java::util::ResourceBundle::getBundle(QString::fromUtf8("\x69\x6e\x74\x65\x72\x61\x63\x74\x69\x76\x65\x2e\x72\x65\x73\x6f\x75\x72\x63\x65\x73\x2e\x49\x6e\x74\x65\x72\x61\x63\x74\x69\x76\x65\x53\x74\x61\x74\x65", 38), hdlg->get_locale());
    if (!finished) {
        QString opt_message = ((resources.getString(QString::fromUtf8("\x62\x61\x74\x63\x68\x5f\x6f\x70\x74\x69\x6d\x69\x7a\x65\x72", 15)) + QString::fromUtf8("\x20", 1)) + resources.getString(QString::fromUtf8("\x73\x74\x6f\x70\x5f\x6d\x65\x73\x73\x61\x67\x65", 12)));
        if (keep_status)
            hdlg->screen_messages->set_add_message(opt_message);
        else
            hdlg->screen_messages->set_status_message(opt_message);
        return;
    }
    QString curr_message = resources.getString(stopped
        ? QString::fromUtf8("\x69\x6e\x74\x65\x72\x72\x75\x70\x74\x65\x64", 11)
        : QString::fromUtf8("\x63\x6f\x6d\x70\x6c\x65\x74\x65\x64", 9));
    QString end_message = ((resources.getString(QString::fromUtf8("\x70\x6f\x73\x74\x72\x6f\x75\x74\x65", 9)) + QString::fromUtf8("\x20", 1)) + curr_message);
    hdlg->screen_messages->set_status_message(end_message);
}

void show_pass(interactive::BoardHandling* hdlg, int pass)
{
    if (hdlg == nullptr || hdlg->screen_messages == nullptr)
        return;
    java::util::ResourceBundle resources = java::util::ResourceBundle::getBundle(QString::fromUtf8("\x69\x6e\x74\x65\x72\x61\x63\x74\x69\x76\x65\x2e\x72\x65\x73\x6f\x75\x72\x63\x65\x73\x2e\x49\x6e\x74\x65\x72\x61\x63\x74\x69\x76\x65\x53\x74\x61\x74\x65", 38), hdlg->get_locale());
    java::lang::Integer* curr_pass_no = java::lang::Integer::valueOf(pass);
    QString start_message = (((((((resources.getString(QString::fromUtf8("\x62\x61\x74\x63\x68\x5f\x61\x75\x74\x6f\x72\x6f\x75\x74\x65\x72", 16)) + QString::fromUtf8("\x20", 1)) + resources.getString(QString::fromUtf8("\x73\x74\x6f\x70\x5f\x6d\x65\x73\x73\x61\x67\x65", 12))) + QString::fromUtf8("\x20\x20\x20\x20\x20\x20\x20\x20", 8)) + resources.getString(QString::fromUtf8("\x70\x61\x73\x73", 4))) + QString::fromUtf8("\x20", 1)) + curr_pass_no->toString()) + QString::fromUtf8("\x3a\x20", 2));
    hdlg->screen_messages->set_status_message(start_message);
}

void show_route(interactive::BoardHandling* hdlg, int to_go, int routed, int ripped, int failed)
{
    if (hdlg == nullptr || hdlg->screen_messages == nullptr)
        return;
    hdlg->screen_messages->set_batch_autoroute_info(to_go, routed, ripped, failed);
}

bool route_open(Snap& snap, Maze& maze, interactive::BoardHandling* hdlg, interactive::Settings* settings, int via_costs, int pass_no,
    const std::function<bool()>& stop, bool fanout_only, int* ripped_out = nullptr)
{
    board::RoutingBoard* board = snap.board;
    if (fanout_only) {
        std::vector<board::Item*> pins;
        for (const SnapItem& it : snap.items) {
            if (it.kind != Kind::Pin || it.net <= 0 || it.item == nullptr)
                continue;
            if (it.layer0 != it.layer1)
                continue;
            bool other_layer = false;
            for (const SnapItem& other : snap.items) {
                if (other.net == it.net && other.component != it.component
                    && (other.layer0 != it.layer0 || other.layer1 != it.layer0))
                    other_layer = true;
            }
            if (other_layer)
                pins.push_back(it.item);
        }
        bool any = false;
        int left = static_cast<int>(pins.size());
        for (board::Item* pin : pins) {
            if (stop())
                return any;
            if (hdlg != nullptr && hdlg->screen_messages != nullptr)
                hdlg->screen_messages->set_batch_fanout_info(pass_no, left);
            int index = -1;
            for (std::size_t i = 0; i < snap.items.size(); ++i) {
                if (snap.items[i].item == pin) {
                    index = static_cast<int>(i);
                    break;
                }
            }
            --left;
            if (index < 0)
                continue;
            std::vector<char> start(snap.items.size(), 0);
            std::vector<char> dest(snap.items.size(), 0);
            start[static_cast<std::size_t>(index)] = 1;
            double limit = std::min(100000.0 * std::pow(2.0, std::max(0, pass_no - 1)), static_cast<double>(std::numeric_limits<int>::max()));
            if (route_pair(snap, maze, settings, via_costs, pass_no, true, snap.items[static_cast<std::size_t>(index)].net, start, dest, stop, limit)) {
                any = true;
                read_snapshot(snap, board, settings, via_costs, pass_no, true);
            }
        }
        return any;
    }
    // wide nets first, while the board is still empty around them
    auto sorted_rows = [&]() {
        std::vector<OpenNet> out = open_nets(snap);
        std::stable_sort(out.begin(), out.end(), [&](const OpenNet& a, const OpenNet& b) {
            return item_half_width(snap, a.net, 0) > item_half_width(snap, b.net, 0);
        });
        return out;
    };
    std::vector<OpenNet> rows = sorted_rows();
    if (board != nullptr && !java::fr_eq(board->get_test_level(), board::TestLevel::RELEASE_VERSION))
        std::cerr << "autoroute2 open " << rows.size() << "\n";
    bool any = false;
    int routed = 0;
    int failed = 0;
    int ripped_total = 0;
    std::vector<char> tried;
    for (std::size_t n = 0; n < rows.size(); ++n) {
        if (stop())
            break;
        // snap is current here and no caller keeps pointers to removed items
        board->free_dropped_items();
        int net = rows[n].net;
        if (net >= static_cast<int>(tried.size()))
            tried.resize(static_cast<std::size_t>(net) + 1, 0);
        if (tried[static_cast<std::size_t>(net)])
            continue;
        tried[static_cast<std::size_t>(net)] = 1;
        show_route(hdlg, static_cast<int>(rows.size() - n), routed, ripped_total, failed);
        note_paint();
        const OpenNet& row = rows[n];
        std::vector<char> start;
        std::vector<char> dest;
        flags_for(snap, row.net, row.comp_a, start);
        flags_for(snap, row.net, row.comp_b, dest);
        bool plane_done = false;
        if (row.plane) {
            for (std::size_t i = 0; i < snap.items.size(); ++i) {
                if (start[i] && snap.items[i].kind == Kind::Plane)
                    plane_done = true;
            }
        }
        if (plane_done)
            continue;
        double limit = std::min(100000.0 * std::pow(2.0, std::max(0, pass_no - 1)), static_cast<double>(std::numeric_limits<int>::max()));
        std::vector<int> ripped_nets;
        if (route_pair(snap, maze, settings, via_costs, pass_no, false, row.net, start, dest, stop, limit,
                snap.ripup ? &ripped_nets : nullptr)) {
            any = true;
            ++routed;
            // like BatchAutorouter: ripped nets already tried in this pass wait for the next one
            ripped_total += static_cast<int>(ripped_nets.size());
            read_snapshot(snap, board, settings, via_costs, pass_no, false);
            rows = sorted_rows();
            n = static_cast<std::size_t>(-1);
        } else
            ++failed;
    }
    show_route(hdlg, 0, routed, ripped_total, failed);
    if (ripped_out != nullptr)
        *ripped_out = ripped_total;
    return any;
}

int via_count(const Snap& snap)
{
    int n = 0;
    for (const SnapItem& it : snap.items)
        n += it.kind == Kind::Via ? 1 : 0;
    return n;
}

double weighted_trace_length(const Snap& snap)
{
    double sum = 0;
    const int32_t cl_class = rules::BoardRules::default_clearance_class();
    for (const SnapItem& it : snap.items) {
        auto* trace = it.kind == Kind::Trace ? dynamic_cast<board::Trace*>(it.item) : nullptr;
        if (trace == nullptr || trace->is_user_fixed())
            continue;
        double w = trace->get_length()
            * (trace->get_half_width() + snap.board->clearance_value(trace->clearance_class_no(), cl_class, trace->get_layer()));
        if (java::fr_eq(trace->get_fixed_state(), board::FixedState::SHOVE_FIXED))
            w /= 2;
        sum += w;
    }
    return sum;
}

bool path_clear(const Snap& s, int layer, int net, int margin, const std::vector<IPt>& path, const std::vector<int>& ignore)
{
    for (std::size_t k = 1; k < path.size(); ++k) {
        if (path[k].x == path[k - 1].x && path[k].y == path[k - 1].y)
            continue;
        if (segment_hits(s, layer, path[k - 1], path[k], net, margin, ignore))
            return false;
    }
    return true;
}

std::vector<IPt> pull_slack(const Snap& s, int layer, int net, int margin, const std::vector<IPt>& in, const std::vector<int>& ignore)
{
    std::vector<IPt> pts = in;
    auto length_of = [](const std::vector<IPt>& path) {
        int64_t sum = 0;
        for (std::size_t i = 1; i < path.size(); ++i) {
            sum += std::abs(static_cast<int64_t>(path[i].x) - path[i - 1].x);
            sum += std::abs(static_cast<int64_t>(path[i].y) - path[i - 1].y);
        }
        return sum;
    };
    auto dedup = [](std::vector<IPt>& path) {
        std::vector<IPt> slim;
        for (const IPt& p : path) {
            if (!slim.empty() && slim.back().x == p.x && slim.back().y == p.y)
                continue;
            if (slim.size() >= 2) {
                IPt a = slim[slim.size() - 2];
                IPt b = slim.back();
                if ((a.x == b.x && b.x == p.x) || (a.y == b.y && b.y == p.y)) {
                    slim.back() = p;
                    continue;
                }
            }
            slim.push_back(p);
        }
        path.swap(slim);
    };
    bool changed = true;
    int guard = 0;
    while (changed && pts.size() >= 4 && guard < 48) {
        ++guard;
        changed = false;
        int64_t before = length_of(pts);
        for (std::size_t i = 1; i + 2 < pts.size(); ++i) {
            IPt p0 = pts[i - 1];
            IPt p1 = pts[i];
            IPt p2 = pts[i + 1];
            IPt p3 = pts[i + 2];
            if (is_anchor(s, p1) || is_anchor(s, p2))
                continue;
            int32_t sx = p2.x - p1.x;
            int32_t sy = p2.y - p1.y;
            if ((sx != 0 && sy != 0) || (sx == 0 && sy == 0))
                continue;
            bool ortho_in = (sx == 0 && p0.y == p1.y) || (sy == 0 && p0.x == p1.x);
            bool ortho_out = (sx == 0 && p2.y == p3.y) || (sy == 0 && p2.x == p3.x);
            if (!ortho_in || !ortho_out)
                continue;
            int32_t d0 = sx == 0 ? p0.x - p1.x : p0.y - p1.y;
            int32_t d3 = sx == 0 ? p3.x - p2.x : p3.y - p2.y;
            if (d0 == 0 || d3 == 0 || (d0 > 0) != (d3 > 0))
                continue;
            int32_t dist = std::min(std::abs(d0), std::abs(d3));
            int sign = d0 > 0 ? 1 : -1;
            auto shifted = [&](IPt p, int32_t delta) {
                if (sx == 0)
                    p.x += delta;
                else
                    p.y += delta;
                return p;
            };
            auto on_stub = [](IPt from, IPt to, IPt q) {
                if (from.x == to.x)
                    return q.x == from.x && (static_cast<int64_t>(q.y - from.y) * (to.y - from.y) >= 0)
                        && std::abs(static_cast<int64_t>(q.y - from.y)) <= std::abs(static_cast<int64_t>(to.y - from.y));
                if (from.y == to.y)
                    return q.y == from.y && (static_cast<int64_t>(q.x - from.x) * (to.x - from.x) >= 0)
                        && std::abs(static_cast<int64_t>(q.x - from.x)) <= std::abs(static_cast<int64_t>(to.x - from.x));
                return false;
            };
            for (int32_t step = dist; step >= 1; step /= 2) {
                int32_t delta = sign * step;
                IPt n1 = shifted(p1, delta);
                IPt n2 = shifted(p2, delta);
                if (!on_stub(p0, p1, n1) || !on_stub(p3, p2, n2)) {
                    if (step == 1)
                        break;
                    continue;
                }
                int steps = std::max(1, step / std::max(1, margin));
                if (steps > 8)
                    steps = 8;
                bool clear = true;
                for (int k = 1; k <= steps && clear; ++k) {
                    int32_t part = static_cast<int32_t>((static_cast<int64_t>(delta) * k) / steps);
                    IPt a = shifted(p1, part);
                    IPt b = shifted(p2, part);
                    if (!(a.x == b.x && a.y == b.y) && segment_hits(s, layer, a, b, net, margin, ignore))
                        clear = false;
                }
                if (clear && !(p0.x == n1.x && p0.y == n1.y) && segment_hits(s, layer, p0, n1, net, margin, ignore))
                    clear = false;
                if (clear && !(p3.x == n2.x && p3.y == n2.y) && segment_hits(s, layer, n2, p3, net, margin, ignore))
                    clear = false;
                if (!clear) {
                    if (step == 1)
                        break;
                    continue;
                }
                std::vector<IPt> saved = pts;
                pts[i] = n1;
                pts[i + 1] = n2;
                dedup(pts);
                if (pts.size() >= 2 && length_of(pts) < before) {
                    changed = true;
                    break;
                }
                pts.swap(saved);
                if (step == 1)
                    break;
            }
            if (changed)
                break;
        }
    }
    dedup(pts);
    return pts;
}

// Keeps the old corners when the board reports more clearance violations than before;
// the snapshot check misses how the board rounds diagonal shapes.
bool replace_trace(Snap& s, board::RoutingBoard* board, SnapItem& it, const std::vector<IPt>& next, int use_w)
{
    auto polyline_of = [](const std::vector<IPt>& corners) {
        java::Array<geometry::planar::Point*> pts(static_cast<int32_t>(corners.size()));
        for (std::size_t k = 0; k < corners.size(); ++k)
            pts[static_cast<int32_t>(k)] = new geometry::planar::IntPoint(corners[k].x, corners[k].y);
        return new geometry::planar::Polyline(pts);
    };
    auto violation_count = [](board::Item* item) {
        auto* v = item != nullptr ? item->clearance_violations() : nullptr;
        const int n = v != nullptr ? v->size() : 0;
        delete v;
        return n;
    };
    java::Array<int32_t> nets(1);
    nets[0] = it.net;
    const int before = violation_count(it.item);
    board->remove_item(it.item);
    it.item = nullptr;
    board::PolylineTrace* placed = board->insert_trace_without_cleaning(polyline_of(next), it.layer0, use_w, nets, it.clearance, board::FixedState::UNFIXED);
    if (placed == nullptr || violation_count(placed) <= before)
        return true;
    board->remove_item(placed);
    board->insert_trace_without_cleaning(polyline_of(it.corners), it.layer0, use_w, nets, it.clearance, board::FixedState::UNFIXED);
    ++s.generation;
    ++s.version;
    return false;
}

void chamfer_routes(Snap& s, board::RoutingBoard* board, interactive::Settings* settings, int via_costs, int pass)
{
    read_snapshot(s, board, settings, via_costs, pass, false, false);
    if (s.angle == 0)
        return;
    std::vector<std::size_t> ids;
    ids.reserve(s.items.size());
    for (std::size_t i = 0; i < s.items.size(); ++i) {
        const SnapItem& it = s.items[i];
        if (it.kind == Kind::Trace && !it.fixed && it.corners.size() >= 3 && it.item != nullptr)
            ids.push_back(i);
    }
    for (std::size_t id : ids) {
        SnapItem& it = s.items[id];
        if (it.item == nullptr || it.corners.size() < 3)
            continue;
        int use_w = trace_half(s, it);
        std::vector<int> ignore(1, static_cast<int>(id));
        // the board rounds oblique trace shapes outwards
        std::vector<IPt> next = miter_polyline(it.corners, [&](IPt a, IPt b) {
            return segment_hits(s, it.layer0, a, b, it.net, use_w + 2, ignore);
        });
        if (next.size() < 2)
            continue;
        bool same = next.size() == it.corners.size();
        for (std::size_t k = 0; same && k < next.size(); ++k)
            same = next[k].x == it.corners[k].x && next[k].y == it.corners[k].y;
        if (same || polyline_degenerate(next))
            continue;
        if (!replace_trace(s, board, it, next, use_w))
            continue;
        set_trace_corners(it, std::move(next), use_w);
        ++s.generation;
        ++s.version;
    }
}

void straighten_routes(Snap& s, board::RoutingBoard* board, interactive::Settings* settings, int via_costs, int pass)
{
    for (int round = 0; round < 8; ++round) {
    read_snapshot(s, board, settings, via_costs, pass, false, false);
    bool any = false;
    std::vector<std::size_t> ids;
    for (std::size_t i = 0; i < s.items.size(); ++i) {
        const SnapItem& it = s.items[i];
        if (it.kind == Kind::Trace && !it.fixed && it.corners.size() >= 4 && it.item != nullptr)
            ids.push_back(i);
    }
    std::sort(ids.begin(), ids.end(), [&](std::size_t a, std::size_t b) {
        return s.items[a].corners.size() > s.items[b].corners.size();
    });
    for (std::size_t id : ids) {
        SnapItem& it = s.items[id];
        if (it.item == nullptr || it.corners.size() < 4)
            continue;
        int use_w = trace_half(s, it);
        std::vector<int> ignore(1, static_cast<int>(id));
        IPt end_a = it.corners.front();
        IPt end_b = it.corners.back();
        for (std::size_t j = 0; j < s.items.size(); ++j) {
            const SnapItem& other = s.items[j];
            if (other.kind != Kind::Pin && other.kind != Kind::Via)
                continue;
            if (!on_layer(other, it.layer0))
                continue;
            bool at_end = (other.center.x == end_a.x && other.center.y == end_a.y)
                || (other.center.x == end_b.x && other.center.y == end_b.y);
            if (at_end)
                ignore.push_back(static_cast<int>(j));
        }
        std::vector<IPt> next = pull_slack(s, it.layer0, it.net, use_w, it.corners, ignore);
        next = collapse_jogs(s, it.layer0, it.net, use_w, next, ignore);
        next = pull_tight(s, it.layer0, it.net, use_w, next, ignore);
        if (!path_clear(s, it.layer0, it.net, use_w, next, ignore))
            continue;
        if (next.size() < 2 || next.front().x != end_a.x || next.front().y != end_a.y || next.back().x != end_b.x
            || next.back().y != end_b.y || next.front().x == next.back().x && next.front().y == next.back().y)
            continue;
        bool same = next.size() == it.corners.size();
        for (std::size_t k = 0; same && k < next.size(); ++k)
            same = next[k].x == it.corners[k].x && next[k].y == it.corners[k].y;
        if (same || polyline_degenerate(next))
            continue;
        if (!replace_trace(s, board, it, next, use_w))
            continue;
        set_trace_corners(it, std::move(next), use_w);
        ++s.generation;
        ++s.version;
        any = true;
    }
    if (!any)
        break;
    }
}

void pull_tight_routes(Snap& s, board::RoutingBoard* board, interactive::Settings* settings, int via_costs, int pass,
    datastructures::Stoppable* stoppable)
{
    (void)stoppable;
    read_snapshot(s, board, settings, via_costs, pass, false, false);
    std::vector<std::size_t> ids;
    for (std::size_t i = 0; i < s.items.size(); ++i) {
        const SnapItem& it = s.items[i];
        if (it.kind == Kind::Trace && !it.fixed && it.corners.size() >= 3 && it.item != nullptr)
            ids.push_back(i);
    }
    for (std::size_t id : ids) {
        SnapItem& it = s.items[id];
        if (it.item == nullptr || it.corners.size() < 3)
            continue;
        int use_w = trace_half(s, it);
        std::vector<int> ignore(1, static_cast<int>(id));
        IPt end_a = it.corners.front();
        IPt end_b = it.corners.back();
        for (std::size_t j = 0; j < s.items.size(); ++j) {
            const SnapItem& other = s.items[j];
            if (other.kind != Kind::Pin && other.kind != Kind::Via)
                continue;
            if (!on_layer(other, it.layer0))
                continue;
            bool at_end = (other.center.x == end_a.x && other.center.y == end_a.y)
                || (other.center.x == end_b.x && other.center.y == end_b.y);
            if (at_end)
                ignore.push_back(static_cast<int>(j));
        }
        std::vector<IPt> next = pull_slack(s, it.layer0, it.net, use_w, it.corners, ignore);
        next = collapse_jogs(s, it.layer0, it.net, use_w, next, ignore);
        next = pull_tight(s, it.layer0, it.net, use_w, next, ignore);
        if (!path_clear(s, it.layer0, it.net, use_w, next, ignore))
            continue;
        if (next.size() < 2 || next.size() > it.corners.size())
            continue;
        if (next.front().x != it.corners.front().x || next.front().y != it.corners.front().y
            || next.back().x != it.corners.back().x || next.back().y != it.corners.back().y)
            continue;
        bool same = next.size() == it.corners.size();
        for (std::size_t k = 0; same && k < next.size(); ++k)
            same = next[k].x == it.corners[k].x && next[k].y == it.corners[k].y;
        if (same || polyline_degenerate(next))
            continue;
        if (!replace_trace(s, board, it, next, use_w))
            continue;
        set_trace_corners(it, std::move(next), use_w);
        ++s.generation;
        ++s.version;
    }
}

} // namespace

Airline current_airline()
{
    Airline a;
    a.valid = g_air_valid.load(std::memory_order_acquire) != 0;
    a.x0 = g_air_x0.load(std::memory_order_relaxed);
    a.y0 = g_air_y0.load(std::memory_order_relaxed);
    a.x1 = g_air_x1.load(std::memory_order_relaxed);
    a.y1 = g_air_y1.load(std::memory_order_relaxed);
    return a;
}

int route_item(board::RoutingBoard* board, board::Item* item, interactive::Settings* settings, int via_costs,
    interactive::InteractiveActionThread* thread)
{
    if (board == nullptr || item == nullptr || item->net_count() <= 0)
        return 2;
    auto stop = [&]() { return thread != nullptr && thread->is_stop_requested(); };
    int net = item->get_net_no(0);
    Snap snap;
    Maze maze;
    read_snapshot(snap, board, settings, via_costs, 1, false);
    int comp = -1;
    for (const SnapItem& it : snap.items) {
        if (it.item == item)
            comp = it.component;
    }
    std::vector<OpenNet> open = open_nets(snap);
    for (const OpenNet& row : open) {
        if (row.net != net)
            continue;
        std::vector<char> start;
        std::vector<char> dest;
        int from = comp >= 0 ? comp : row.comp_a;
        int to = from == row.comp_a ? row.comp_b : row.comp_a;
        flags_for(snap, net, from, start);
        flags_for(snap, net, to, dest);
        if (route_pair(snap, maze, settings, via_costs, 1, false, net, start, dest, stop, 100000.0))
            return 1;
        return 0;
    }
    return 2;
}

int fanout_pin(board::RoutingBoard* board, board::Pin* pin, interactive::Settings* settings, int ripup_costs,
    interactive::InteractiveActionThread* thread)
{
    if (board == nullptr || pin == nullptr || pin->net_count() != 1)
        return 2;
    if (pin->first_layer() != pin->last_layer())
        return 2;
    auto stop = [&]() { return thread != nullptr && thread->is_stop_requested(); };
    Snap snap;
    Maze maze;
    read_snapshot(snap, board, settings, std::max(1, ripup_costs), 1, true);
    std::vector<char> start(snap.items.size(), 0);
    std::vector<char> dest(snap.items.size(), 0);
    bool found = false;
    for (std::size_t i = 0; i < snap.items.size(); ++i) {
        if (snap.items[i].item == pin) {
            start[i] = 1;
            found = true;
        }
    }
    if (!found)
        return 0;
    if (route_pair(snap, maze, settings, std::max(1, ripup_costs), 1, true, pin->get_net_no(0), start, dest, stop, 100000.0))
        return 1;
    return 0;
}

int pin_components(const Snap& snap, int net)
{
    std::vector<int> ids;
    for (const SnapItem& it : snap.items) {
        if (it.kind == Kind::Pin && it.net == net && it.component >= 0)
            ids.push_back(it.component);
    }
    std::sort(ids.begin(), ids.end());
    ids.erase(std::unique(ids.begin(), ids.end()), ids.end());
    return static_cast<int>(ids.size());
}

int pin_incompletes(const Snap& snap)
{
    std::vector<int> nets;
    for (const SnapItem& it : snap.items) {
        if (it.kind == Kind::Pin && it.net > 0)
            nets.push_back(it.net);
    }
    std::sort(nets.begin(), nets.end());
    nets.erase(std::unique(nets.begin(), nets.end()), nets.end());
    int sum = 0;
    for (int net : nets) {
        int n = pin_components(snap, net);
        if (n > 1)
            sum += n - 1;
    }
    return sum;
}

board::Item* flagged_end(const Snap& snap, const std::vector<char>& flags)
{
    board::Item* any = nullptr;
    for (std::size_t i = 0; i < flags.size() && i < snap.items.size(); ++i) {
        if (flags[i] == 0 || snap.items[i].item == nullptr)
            continue;
        if (snap.items[i].kind == Kind::Pin)
            return snap.items[i].item;
        if (any == nullptr)
            any = snap.items[i].item;
    }
    return any;
}

int component_of(const Snap& snap, board::Item* item)
{
    if (item == nullptr)
        return -1;
    for (const SnapItem& it : snap.items) {
        if (it.item == item)
            return it.component;
    }
    return -1;
}

void add_rip_set(std::vector<std::vector<board::Item*>>& sets, std::vector<board::Item*> items)
{
    std::sort(items.begin(), items.end());
    items.erase(std::unique(items.begin(), items.end()), items.end());
    if (items.empty() || items.size() > 6 || sets.size() >= 6)
        return;
    for (const std::vector<board::Item*>& have : sets) {
        if (have == items)
            return;
    }
    sets.push_back(std::move(items));
}

void collect_rip_sets(Snap& snap, int net, const std::vector<char>& start, const std::vector<char>& dest,
    const std::function<bool()>& stop, std::vector<std::vector<board::Item*>>& sets)
{
    struct PinAt {
        IPt at;
        int layer0 = 0;
        int layer1 = 0;
        int pad = 0;
    };
    std::vector<PinAt> pins;
    for (std::size_t i = 0; i < snap.items.size(); ++i) {
        bool side = (i < start.size() && start[i] != 0) || (i < dest.size() && dest[i] != 0);
        if (!side || snap.items[i].kind != Kind::Pin)
            continue;
        PinAt pin;
        pin.at = snap.items[i].center;
        pin.layer0 = snap.items[i].layer0;
        pin.layer1 = snap.items[i].layer1;
        pin.pad = std::max(snap.items[i].box.x1 - snap.items[i].box.x0, snap.items[i].box.y1 - snap.items[i].box.y0) / 2;
        pins.push_back(pin);
    }
    int half = std::max(1, item_half_width(snap, net, 0));
    struct Near {
        double dist2 = 0;
        board::Item* item = nullptr;
    };
    std::vector<Near> near;
    for (const SnapItem& it : snap.items) {
        if (it.kind != Kind::Trace || it.fixed || it.item == nullptr || it.net == net || it.net <= 0 || it.corners.size() < 2)
            continue;
        int other = item_half_width(snap, it.net, it.layer0);
        int clr = pair_clearance(snap, 1, it.clearance, it.layer0);
        double best = std::numeric_limits<double>::infinity();
        for (std::size_t k = 1; k < it.corners.size(); ++k) {
            for (const PinAt& pin : pins) {
                if (it.layer0 < pin.layer0 || it.layer0 > pin.layer1)
                    continue;
                double lim = static_cast<double>(half + other + clr + pin.pad);
                double dist2 = dist2_seg(it.corners[k - 1], it.corners[k], pin.at.x, pin.at.y);
                if (dist2 <= lim * lim && dist2 < best)
                    best = dist2;
            }
        }
        if (best < std::numeric_limits<double>::infinity())
            near.push_back(Near{best, it.item});
    }
    std::sort(near.begin(), near.end(), [](const Near& a, const Near& b) { return a.dist2 < b.dist2; });
    for (std::size_t i = 0; i < near.size() && i < 4; ++i)
        add_rip_set(sets, {near[i].item});
    if (near.size() >= 2)
        add_rip_set(sets, {near[0].item, near[1].item});
    if (stop() || sets.size() >= 6)
        return;
    snap.half_w = half;
    snap.fanout = false;
    snap.forbid_rip.assign(snap.items.size(), 0);
    Maze rip_maze;
    std::vector<int> unused;
    for (int layer = 0; layer < snap.layers; ++layer) {
        if (layer < static_cast<int>(snap.layer_on.size()) && snap.layer_on[static_cast<std::size_t>(layer)] == 0)
            continue;
        build_rooms(snap, net, layer, half, true, start, dest, rip_maze, unused, false);
        link_doors(rip_maze, layer, half);
    }
    build_drills(snap, rip_maze, net);
    if (rip_maze.rooms.size() > 120000) {
        snap.forbid_rip.clear();
        return;
    }
    for (int wave = 0; wave < 4 && sets.size() < 6 && !stop(); ++wave) {
        if (wave > 0) {
            rip_maze.clear_wave();
            for (int layer = 0; layer < snap.layers; ++layer) {
                if (layer < static_cast<int>(snap.layer_on.size()) && snap.layer_on[static_cast<std::size_t>(layer)] == 0)
                    continue;
                mark_terminals(snap, rip_maze, layer, start, false);
                mark_terminals(snap, rip_maze, layer, dest, true);
            }
        }
        auto deadline = std::chrono::steady_clock::now() + std::chrono::seconds(8);
        Found found = search_wave(snap, rip_maze, net, half, deadline, stop);
        std::vector<board::Item*> ripped;
        for (int id : found.rip_items) {
            if (id < 0 || id >= static_cast<int>(snap.items.size()))
                continue;
            const SnapItem& it = snap.items[static_cast<std::size_t>(id)];
            if (it.kind != Kind::Trace || it.fixed || it.item == nullptr || it.net == net)
                continue;
            ripped.push_back(it.item);
        }
        if (ripped.empty())
            break;
        add_rip_set(sets, ripped);
        for (board::Item* item : ripped) {
            for (std::size_t i = 0; i < snap.items.size() && i < snap.forbid_rip.size(); ++i) {
                if (snap.items[i].item == item)
                    snap.forbid_rip[i] = 1;
            }
        }
    }
    snap.forbid_rip.clear();
}

struct SavedTrace {
    std::vector<IPt> corners;
    int net = 0;
    int layer = 0;
    int half = 0;
    int clearance = 0;
};

bool jog_trace(Snap& snap, const SavedTrace& saved, int target_net)
{
    if (saved.corners.size() < 2 || snap.board == nullptr)
        return false;
    struct Threat {
        IPt at;
        int pad = 0;
    };
    std::vector<Threat> pins;
    for (const SnapItem& it : snap.items) {
        if (it.kind != Kind::Pin || it.net != target_net)
            continue;
        if (it.layer0 > saved.layer || saved.layer > it.layer1)
            continue;
        Threat pin;
        pin.at = it.center;
        pin.pad = std::max(it.box.x1 - it.box.x0, it.box.y1 - it.box.y0) / 2;
        pins.push_back(pin);
    }
    if (pins.empty())
        return false;
    int clr = pair_clearance(snap, 1, saved.clearance, saved.layer);
    std::vector<IPt> path = saved.corners;
    bool bowed = false;
    for (std::size_t seg = 1; seg < path.size(); ++seg) {
        IPt a = path[seg - 1];
        IPt b = path[seg];
        double dx = static_cast<double>(b.x - a.x);
        double dy = static_cast<double>(b.y - a.y);
        double len = std::sqrt(dx * dx + dy * dy);
        if (len < 2)
            continue;
        double ux = dx / len;
        double uy = dy / len;
        double px = -uy;
        double py = ux;
        double shift = 0;
        double t_min = len;
        double t_max = 0;
        bool threat = false;
        for (const Threat& pin : pins) {
            int need = pin.pad + saved.half + clr + 80;
            double t = (static_cast<double>(pin.at.x - a.x) * ux) + (static_cast<double>(pin.at.y - a.y) * uy);
            if (t < 0)
                t = 0;
            if (t > len)
                t = len;
            double qx = static_cast<double>(a.x) + ux * t;
            double qy = static_cast<double>(a.y) + uy * t;
            double vx = static_cast<double>(pin.at.x) - qx;
            double vy = static_cast<double>(pin.at.y) - qy;
            double dist = std::sqrt(vx * vx + vy * vy);
            if (dist >= need)
                continue;
            threat = true;
            shift = std::max(shift, static_cast<double>(need) - dist);
            double pad = static_cast<double>(need);
            t_min = std::min(t_min, t - pad);
            t_max = std::max(t_max, t + pad);
        }
        if (!threat || shift < 1)
            continue;
        if (t_min < 0)
            t_min = 0;
        if (t_max > len)
            t_max = len;
        auto bow_at = [&](double t, double sign) {
            IPt p;
            p.x = static_cast<int32_t>(std::llround(static_cast<double>(a.x) + ux * t + sign * px * shift));
            p.y = static_cast<int32_t>(std::llround(static_cast<double>(a.y) + uy * t + sign * py * shift));
            return p;
        };
        std::vector<int> none;
        auto clear = [&](const std::vector<IPt>& extra) {
            std::vector<IPt> trial;
            trial.push_back(a);
            for (const IPt& p : extra)
                trial.push_back(p);
            trial.push_back(b);
            for (std::size_t i = 1; i < trial.size(); ++i) {
                if (trial[i].x == trial[i - 1].x && trial[i].y == trial[i - 1].y)
                    continue;
                if (segment_hits(snap, saved.layer, trial[i - 1], trial[i], saved.net, saved.half, none))
                    return false;
            }
            return true;
        };
        std::vector<IPt> extra;
        const bool ortho = snap.angle < 2 && (a.x == b.x || a.y == b.y);
        IPt q0 = bow_at(t_min, 0);
        IPt q1 = bow_at(t_max, 0);
        if (ortho) {
            if (a.x == b.x) {
                q0.x = a.x;
                q1.x = a.x;
            } else {
                q0.y = a.y;
                q1.y = a.y;
            }
        }
        for (double sign : {1.0, -1.0}) {
            IPt p0 = bow_at(t_min, sign);
            IPt p1 = bow_at(t_max, sign);
            if (ortho) {
                if (a.x == b.x) {
                    p0.y = q0.y;
                    p1.y = q1.y;
                } else {
                    p0.x = q0.x;
                    p1.x = q1.x;
                }
            }
            std::vector<IPt> trial = ortho ? std::vector<IPt>{q0, p0, p1, q1} : std::vector<IPt>{p0, p1};
            if (clear(trial)) {
                extra = trial;
                break;
            }
        }
        if (extra.empty())
            continue;
        std::vector<IPt> next;
        next.insert(next.end(), path.begin(), path.begin() + static_cast<std::ptrdiff_t>(seg));
        for (const IPt& p : extra) {
            if (next.empty() || next.back().x != p.x || next.back().y != p.y)
                next.push_back(p);
        }
        next.insert(next.end(), path.begin() + static_cast<std::ptrdiff_t>(seg), path.end());
        path.swap(next);
        bowed = true;
        break;
    }
    if (!bowed || path.size() < 2 || polyline_degenerate(path))
        return false;
    java::Array<geometry::planar::Point*> pts(static_cast<int32_t>(path.size()));
    for (std::size_t k = 0; k < path.size(); ++k)
        pts[static_cast<int32_t>(k)] = new geometry::planar::IntPoint(path[k].x, path[k].y);
    java::Array<int32_t> nets(1);
    nets[0] = saved.net;
    geometry::planar::Polyline* poly = new geometry::planar::Polyline(pts);
    snap.board->insert_trace_without_cleaning(poly, saved.layer, saved.half, nets, saved.clearance, board::FixedState::UNFIXED);
    return true;
}

struct RipScore {
    bool ok = false;
    int rerouted = 0;
    int after = 0;
};

bool rip_remaining(Snap& snap, Maze& maze, interactive::BoardHandling* hdlg, interactive::Settings* settings, int via_costs,
    int pass_no, const std::function<bool()>& stop, int depth);

RipScore try_rip_set(Snap& snap, Maze& maze, interactive::BoardHandling* hdlg, interactive::Settings* settings, int via_costs, int pass_no, int net,
    board::Item* end_a, board::Item* end_b, const std::vector<board::Item*>& ripped, const std::function<bool()>& stop,
    double max_ms, bool keep, int depth)
{
    RipScore score;
    if (snap.board == nullptr || ripped.empty() || end_a == nullptr || end_b == nullptr)
        return score;
    int before = pin_incompletes(snap);
    std::vector<board::Item*> doomed;
    std::vector<SavedTrace> saved;
    auto add_doomed = [&](board::Item* item) {
        if (item == nullptr || !item->is_route() || item->is_user_fixed())
            return;
        for (board::Item* have : doomed) {
            if (have == item)
                return;
        }
        doomed.push_back(item);
    };
    for (board::Item* item : ripped) {
        add_doomed(item);
        for (const SnapItem& it : snap.items) {
            if (it.item != item || it.corners.size() < 2)
                continue;
            SavedTrace row;
            row.corners = it.corners;
            row.net = it.net;
            row.layer = it.layer0;
            auto* trace = dynamic_cast<board::Trace*>(item);
            row.half = trace != nullptr ? std::max(1, static_cast<int>(trace->get_half_width())) : item_half_width(snap, it.net, it.layer0);
            row.clearance = it.clearance;
            saved.push_back(std::move(row));
            break;
        }
    }
    if (doomed.empty())
        return score;
    std::vector<int> victims;
    std::vector<int> comp_before;
    for (board::Item* item : doomed) {
        int vnet = 0;
        for (const SnapItem& it : snap.items) {
            if (it.item == item) {
                vnet = it.net;
                break;
            }
        }
        if (vnet <= 0 || vnet == net)
            continue;
        bool seen = false;
        for (int have : victims)
            seen = seen || have == vnet;
        if (seen)
            continue;
        victims.push_back(vnet);
        comp_before.push_back(pin_components(snap, vnet));
    }
    std::vector<int> pending;
    pending.push_back(net);
    for (const OpenNet& row : open_nets(snap)) {
        if (row.net == net || row.plane)
            continue;
        bool victim = false;
        for (int vnet : victims)
            victim = victim || vnet == row.net;
        if (!victim)
            pending.push_back(row.net);
    }
    int target_before = pin_components(snap, net);
    snap.board->generate_snapshot();
    for (board::Item* item : doomed)
        snap.board->remove_item(item);
    read_snapshot(snap, snap.board, settings, via_costs, pass_no, false);
    for (const SavedTrace& row : saved) {
        if (!jog_trace(snap, row, net))
            continue;
        read_snapshot(snap, snap.board, settings, via_costs, pass_no, false);
    }
    int rerouted = 0;
    for (std::size_t i = 0; i < victims.size(); ++i) {
        int now = pin_components(snap, victims[i]);
        if (now > comp_before[i])
            rerouted += now - comp_before[i];
    }
    snap.board->generate_snapshot();
    auto route_nets = [&](const std::vector<int>& nets, int attempts) {
        for (int n : nets) {
            for (int attempt = 0; attempt < attempts && !stop(); ++attempt) {
                std::vector<OpenNet> rows = open_nets(snap);
                bool found_row = false;
                for (const OpenNet& row : rows) {
                    if (row.net != n || row.plane)
                        continue;
                    std::vector<char> start;
                    std::vector<char> dest;
                    flags_for(snap, n, row.comp_a, start);
                    flags_for(snap, n, row.comp_b, dest);
                    route_pair(snap, maze, settings, via_costs, pass_no, false, n, start, dest, stop, max_ms);
                    read_snapshot(snap, snap.board, settings, via_costs, pass_no, false);
                    found_row = true;
                    break;
                }
                if (!found_row)
                    break;
            }
        }
    };
    route_nets(pending, 4);
    route_nets(victims, 4);
    int target_after = pin_components(snap, net);
    int after_pins = pin_incompletes(snap);
    int levels = 2;
    if (target_after < target_before && after_pins >= before && !stop()) {
        snap.board->undo(nullptr);
        read_snapshot(snap, snap.board, settings, via_costs, pass_no, false);
        --levels;
        route_nets(victims, 4);
        route_nets(pending, 4);
        target_after = pin_components(snap, net);
        after_pins = pin_incompletes(snap);
    }
    if (depth == 0 && target_after < target_before && after_pins >= before && after_pins <= 2 && !stop()) {
        rip_remaining(snap, maze, hdlg, settings, via_costs, pass_no, stop, depth + 1);
        target_after = pin_components(snap, net);
        after_pins = pin_incompletes(snap);
    }
    score.ok = target_after < target_before && after_pins < before;
    score.rerouted = rerouted;
    score.after = after_pins;
    auto pop_both = [&]() {
        snap.board->pop_snapshot();
        if (snap.board->components != nullptr && snap.board->components->undo_list != nullptr)
            snap.board->components->undo_list->pop_snapshot();
    };
    if (keep && score.ok) {
        for (int level = 0; level < levels; ++level)
            pop_both();
    } else {
        for (int level = 0; level < levels; ++level)
            snap.board->undo(nullptr);
    }
    read_snapshot(snap, snap.board, settings, via_costs, pass_no, false);
    return score;
}

bool rip_remaining(Snap& snap, Maze& maze, interactive::BoardHandling* hdlg, interactive::Settings* settings, int via_costs,
    int pass_no, const std::function<bool()>& stop, int depth)
{
    int before_all = pin_incompletes(snap);
    if (before_all <= 0 || snap.board == nullptr)
        return false;
    double max_ms = std::min(100000.0 * std::pow(2.0, std::max(0, pass_no - 1)), static_cast<double>(std::numeric_limits<int>::max()));
    bool any = false;
    for (int round = 0; round < 6 && !stop(); ++round) {
        read_snapshot(snap, snap.board, settings, via_costs, pass_no, false);
        if (pin_incompletes(snap) <= 0)
            break;
        std::vector<OpenNet> rows = open_nets(snap);
        bool improved = false;
        for (const OpenNet& row : rows) {
            if (stop() || row.plane)
                continue;
            std::vector<char> start;
            std::vector<char> dest;
            flags_for(snap, row.net, row.comp_a, start);
            flags_for(snap, row.net, row.comp_b, dest);
            board::Item* end_a = flagged_end(snap, start);
            board::Item* end_b = flagged_end(snap, dest);
            std::vector<std::vector<board::Item*>> sets;
            collect_rip_sets(snap, row.net, start, dest, stop, sets);
            RipScore best;
            std::vector<board::Item*> best_set;
            for (const std::vector<board::Item*>& set : sets) {
                if (stop())
                    break;
                RipScore score = try_rip_set(snap, maze, hdlg, settings, via_costs, pass_no, row.net, end_a, end_b, set, stop, max_ms, false, depth);
                if (!score.ok)
                    continue;
                if (!best.ok || score.rerouted < best.rerouted || (score.rerouted == best.rerouted && score.after < best.after)) {
                    best = score;
                    best_set = set;
                }
                if (best.ok && best.rerouted == 0 && best.after == 0)
                    break;
            }
            if (!best.ok)
                continue;
            RipScore kept = try_rip_set(snap, maze, hdlg, settings, via_costs, pass_no, row.net, end_a, end_b, best_set, stop, max_ms, true, depth);
            if (!kept.ok)
                continue;
            improved = true;
            any = true;
            show_route(hdlg, static_cast<int>(rows.size()), 1, kept.rerouted, 0);
            break;
        }
        if (!improved)
            break;
    }
    read_snapshot(snap, snap.board, settings, via_costs, pass_no, false);
    return any && pin_incompletes(snap) < before_all;
}

bool run_session(interactive::BoardHandling* hdlg, interactive::InteractiveActionThread* thread)
{
    if (hdlg == nullptr || hdlg->get_routing_board() == nullptr || hdlg->settings == nullptr)
        return false;
    board::RoutingBoard* board = hdlg->get_routing_board();
    interactive::Settings* settings = hdlg->settings;
    auto stop = [&]() { return thread != nullptr && thread->is_stop_requested(); };
    PaintScope painting(hdlg);
    struct DroppedScope {
        board::RoutingBoard* board;
        explicit DroppedScope(board::RoutingBoard* b) : board(b) { board->item_list->track_dropped = true; }
        ~DroppedScope()
        {
            board->free_dropped_items();
            board->item_list->track_dropped = false;
            board->item_list->dropped.clear();
        }
    } dropped_scope(board);
    if (!pins_have_rooms(board, settings) && board->get_test_level() != board::TestLevel::RELEASE_VERSION)
        std::cerr << "autoroute2: no free room touches a pin\n";
    int pass = std::max(1, static_cast<int>(settings->autoroute_settings->get_pass_no()));
    int via_costs = settings->autoroute_settings->get_via_costs();
    const int start_ripup = std::max(1, static_cast<int>(settings->autoroute_settings->get_start_ripup_costs()));
    Snap snap;
    Maze maze;
    if (settings->autoroute_settings->get_with_fanout() && pass <= 1 && !stop()) {
        read_snapshot(snap, board, settings, via_costs, pass, true);
        route_open(snap, maze, hdlg, settings, via_costs, pass, stop, true);
    }
    int stalled = 0;
    bool rip_frozen = false;
    int passes_done = 0;
    int open_at_start = -1;
    if (settings->autoroute_settings->get_with_autoroute()) {
        while (!stop() && stalled < 6 && pass < 30) {
            show_pass(hdlg, pass);
            read_snapshot(snap, board, settings, via_costs, pass, false);
            if (open_at_start < 0)
                open_at_start = pin_incompletes(snap);
            if (open_nets(snap).empty())
                break;
            ++passes_done;
            int before = pin_incompletes(snap);
            int ripped = 0;
            bool progressed = route_open(snap, maze, hdlg, settings, via_costs, pass, stop, false, &ripped);
            if (open_nets(snap).empty())
                break;
            int mid = pin_incompletes(snap);
            if (mid < before)
                rip_frozen = false;
            // ripping two nets and routing two others counts as progress, but leaves the open count unchanged
            const bool stuck = !progressed || (stalled > 0 && mid >= before);
            if (stuck && !rip_frozen && !stop()) {
                if (rip_remaining(snap, maze, hdlg, settings, via_costs, pass, stop, 0))
                    progressed = true;
                else if (pin_incompletes(snap) >= mid)
                    rip_frozen = true;
            }
            if (open_nets(snap).empty())
                break;
            int after = pin_incompletes(snap);
            if (after < before || (progressed && ripped == 0))
                stalled = 0;
            else
                ++stalled;
            settings->autoroute_settings->increment_pass_no();
            ++pass;
        }
    }
    if (open_at_start >= 0) {
        const int failed = pin_incompletes(snap);
        const int routed = std::max(0, open_at_start - failed);
        show_autoroute_result(hdlg, passes_done, routed, failed);
    }
    if (settings->autoroute_settings->get_with_postroute() && !stop()) {
        show_postroute(hdlg, false, false, open_at_start >= 0);
        note_paint_now();
        bool increased = true;
        bool improved = true;
        int opt_pass = 0;
        while (improved && !stop() && opt_pass < 40) {
            ++opt_pass;
            improved = false;
            snap.flat_dir = (opt_pass % 2) == 0;
            read_snapshot(snap, board, settings, via_costs, pass, false);
            // connections without any trace are never picked below, so try them directly first
            std::set<int> tried;
            for (bool routed_one = true; routed_one && !stop();) {
                routed_one = false;
                for (const OpenNet& row : open_nets(snap)) {
                    if (row.plane || !tried.insert(row.net).second)
                        continue;
                    std::vector<char> start;
                    std::vector<char> dest;
                    flags_for(snap, row.net, row.comp_a, start);
                    flags_for(snap, row.net, row.comp_b, dest);
                    route_pair(snap, maze, settings, via_costs, pass, false, row.net, start, dest, stop, 100000.0);
                    read_snapshot(snap, board, settings, via_costs, pass, false);
                    routed_one = true;
                    break;
                }
            }
            double len_before = weighted_trace_length(snap);
            int open_before = pin_incompletes(snap);
            int vias_before = via_count(snap);
            // BatchOptRoute order: vias by x, then traces without via contact by their right end
            // by id, because undo puts clones in place of the items changed meanwhile
            struct OptSeed {
                int id;
                IPt at;
                int layer;
                bool via;
            };
            std::vector<OptSeed> order;
            for (const SnapItem& it : snap.items) {
                if (it.item == nullptr || it.fixed)
                    continue;
                if (it.kind == Kind::Via) {
                    order.push_back({it.item->get_id_no(), it.center, it.layer0, true});
                } else if (it.kind == Kind::Trace && it.corners.size() >= 2) {
                    auto* trace = dynamic_cast<board::Trace*>(it.item);
                    if (trace == nullptr || trace->is_shove_fixed())
                        continue;
                    bool at_via = false;
                    java::util::TreeSet<board::Item*>* contacts = trace->get_normal_contacts();
                    if (contacts != nullptr) {
                        for (auto* c : java::iterate(contacts)) {
                            board::Item* ci = java::narrow<board::Item*>(c);
                            at_via = at_via || (dynamic_cast<board::Via*>(ci) != nullptr && !ci->is_user_fixed());
                        }
                        delete contacts;
                    }
                    if (at_via)
                        continue;
                    IPt a = it.corners.front();
                    IPt b = it.corners.back();
                    bool a_first = a.x < b.x || (a.x == b.x && a.y < b.y);
                    order.push_back({it.item->get_id_no(), a_first ? b : a, it.layer0, false});
                }
            }
            std::stable_sort(order.begin(), order.end(), [](const OptSeed& l, const OptSeed& r) {
                if (l.at.x != r.at.x)
                    return l.at.x < r.at.x;
                if (l.at.y != r.at.y)
                    return l.at.y < r.at.y;
                if (l.layer != r.layer)
                    return l.layer < r.layer;
                return l.via && !r.via;
            });
            std::set<int> done;
            for (const OptSeed& seed : order) {
                if (stop())
                    break;
                if (done.count(seed.id) != 0)
                    continue;
                board::Item* item = nullptr;
                int net = 0;
                for (const SnapItem& it : snap.items) {
                    if (it.item != nullptr && it.item->get_id_no() == seed.id) {
                        item = it.item;
                        net = it.net;
                        break;
                    }
                }
                if (item == nullptr || net <= 0)
                    continue;
                // like BatchOptRoute: rip the whole connections, for traces also those of the fork contacts
                std::vector<board::Item*> ripped{item};
                if (auto* trace = dynamic_cast<board::Trace*>(item)) {
                    for (int side = 0; side < 2; ++side) {
                        java::util::TreeSet<board::Item*>* contacts = side == 0 ? trace->get_start_contacts() : trace->get_end_contacts();
                        if (contacts == nullptr)
                            continue;
                        std::vector<board::Item*> list;
                        bool only_traces = true;
                        for (auto* c : java::iterate(contacts)) {
                            board::Item* ci = java::narrow<board::Item*>(c);
                            only_traces = only_traces && ci != nullptr && !ci->is_user_fixed() && dynamic_cast<board::Trace*>(ci) != nullptr;
                            list.push_back(ci);
                        }
                        delete contacts;
                        if (only_traces)
                            ripped.insert(ripped.end(), list.begin(), list.end());
                    }
                }
                std::vector<board::Item*> members;
                std::set<board::Item*> seen;
                bool fixed = false;
                for (board::Item* r : ripped) {
                    java::util::TreeSet<board::Item*>* conn = r->get_connection_items(board::Item_StopConnectionOption::NONE);
                    if (conn == nullptr)
                        continue;
                    for (auto* member : java::iterate(conn)) {
                        board::Item* m = java::narrow<board::Item*>(member);
                        if (m == nullptr || !m->is_route() || !seen.insert(m).second)
                            continue;
                        fixed = fixed || m->is_user_fixed();
                        members.push_back(m);
                    }
                    delete conn;
                }
                done.insert(seed.id);
                if (fixed || members.empty())
                    continue;
                board->generate_snapshot();
                for (board::Item* m : members)
                    board->remove_item(m);
                // like BatchOptRoute: up to six passes over everything open, ripping allowed
                int rip_start = start_ripup * (increased ? 10 : 1);
                if (!seed.via)
                    rip_start = static_cast<int>(std::lround(0.6 * rip_start));
                snap.ripup_start = std::max(1, rip_start);
                for (int inner = 1; inner <= 6 && !stop(); ++inner) {
                    read_snapshot(snap, board, settings, via_costs, inner, false, false);
                    if (open_nets(snap).empty())
                        break;
                    if (!route_open(snap, maze, nullptr, settings, via_costs, inner, stop, false))
                        break;
                }
                snap.ripup_start = 0;
                read_snapshot(snap, board, settings, via_costs, pass, false, false);
                int open_now = pin_incompletes(snap);
                int vias_now = via_count(snap);
                double len_now = weighted_trace_length(snap);
                bool better = !stop()
                    && (open_now < open_before
                        || (open_now == open_before && (vias_now < vias_before || (vias_now == vias_before && len_now < len_before))));
                if (!better) {
                    for (board::Item* m : members)
                        done.insert(m->get_id_no());
                    board->undo(nullptr);
                    read_snapshot(snap, board, settings, via_costs, pass, false, true);
                    continue;
                }
                board->pop_snapshot();
                if (board->components != nullptr && board->components->undo_list != nullptr)
                    board->components->undo_list->pop_snapshot();
                improved = true;
                open_before = open_now;
                vias_before = vias_now;
                len_before = len_now;
                read_snapshot(snap, board, settings, via_costs, pass, false, true);
                note_paint();
            }
            if (increased && !improved) {
                increased = false;
                improved = true;
            }
        }
        snap.flat_dir = false;
        show_postroute(hdlg, true, stop());
    }
    if (!stop())
        straighten_routes(snap, board, settings, via_costs, pass);
    if (!stop())
        chamfer_routes(snap, board, settings, via_costs, pass);
    if (!stop())
        pull_tight_routes(snap, board, settings, via_costs, pass, static_cast<datastructures::Stoppable*>(thread));
    return !stop();
}

} // namespace autoroute2
