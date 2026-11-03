/*
 * Copyright (C) 2014 Alfons Wirtz — C++/Qt port of FreeRouting (GPLv3)
 */
#include <QtWidgets/QApplication>
#include <QtCore/QCoreApplication>
#include <QtWidgets/QMenu>
#include <QtWidgets/QMenuBar>
#include <QtGui/QGuiApplication>
#include <QtGui/QCursor>
#include <QtGui/QWindow>
#include <QtCore/QThread>
#include <QtCore/QFileInfo>
#include <QtCore/QDir>
#include <QtGui/QImage>
#include <QtGui/QWheelEvent>
#include <QtCore/QItemSelection>
#include <algorithm>
#include <cmath>
#include <iostream>
#include <typeinfo>
#include <vector>
#include "jcompat/jcompat.h"
#include "autoroute/BumpArena.h"
#include "jcompat/java_math.h"
#include "jcompat/java_util.h"
#include "geometry/planar/Limits.h"
#include "geometry/planar/IntPoint.h"
#include "geometry/planar/IntBox.h"
#include "geometry/planar/FloatPoint.h"
#include "geometry/planar/IntOctagon.h"
#include "geometry/planar/Polyline.h"
#include "geometry/planar/Point.h"
#include "geometry/planar/OrthogonalBoundingDirections.h"
#include "datastructures/MinAreaTree.h"
#include "datastructures/BigIntAux.h"
#include "interactive/BoardHandling.h"
#include "interactive/AutorouteSettings.h"
#include "debug/debugMemoryLeak.h"
#include "board/AngleRestriction.h"
#include "rules/NetClass.h"
#include "rules/NetClasses.h"
#include "interactive/ScreenMessages.h"
#include "interactive/InteractiveActionThread.h"
#include "interactive/RatsNest.h"
#include "gui/BoardPanel.h"
#include "gui/BoardFrame.h"
#include "gui/BoardToolbar.h"
#include "gui/BoardToolbarSelectedItem.h"
#include "gui/PopupMenuDynamicRoute.h"
#include "gui/PopupMenuStitchRoute.h"
#include "gui/PopupMenuChangeLayer.h"
#include "gui/MainApplication.h"
#include "gui/DesignFile.h"
#include "gui/BoardPanel.h"
#include "gui/BoardFrame.h"
#include "gui/WindowClearanceMatrix.h"
#include "gui/ColorManager.h"
#include "gui/WindowVia.h"
#include "gui/WindowNetClasses.h"
#include "gui/ComboBoxLayer.h"
#include "gui/WindowAssignNetClass.h"
#include "gui/WindowEditVias.h"
#include "gui/WindowNetClasses.h"
#include "gui/GUIDefaultsFile.h"
#include "gui/PopupMenuDisplay.h"
#include "gui/BoardMenuBar.h"
#include "gui/BoardMenuFile.h"
#include "interactive/SelectMenuState.h"
#include "interactive/RouteMenuState.h"
#include "interactive/RouteState.h"
#include "interactive/DynamicRouteState.h"
#include "interactive/StitchRouteState.h"
#include "interactive/Route.h"
#include "interactive/Settings.h"
#include "interactive/DragMenuState.h"
#include "interactive/Logfile.h"
#include "board/BoardOutline.h"
#include "board/ClearanceViolation.h"
#include "geometry/planar/ConvexShape.h"
#include "board/ComponentOutline.h"
#include "board/ConductionArea.h"
#include "board/ObstacleArea.h"
#include "board/ViaObstacleArea.h"
#include "board/ComponentObstacleArea.h"
#include "boardgraphics/CoordinateTransform.h"
#include "boardgraphics/GraphicsContext.h"
#include "boardgraphics/ColorIntensityTable.h"
#include "gui/WindowObjectVisibility.h"
#include <QtGui/QMouseEvent>
#include <QtGui/QKeyEvent>
#include <QtGui/QPainter>
#include <QtCore/QDir>
#include <QtCore/QTemporaryDir>
#include "designformats/specctra/DsnFile.h"
#include "designformats/specctra/SpecctraFileScanner.h"
#include "designformats/specctra/Keyword.h"
#include "board/BoardObserverAdaptor.h"
#include "board/ItemIdNoGenerator.h"
#include "board/TestLevel.h"
#include "board/RoutingBoard.h"
#include "board/Item.h"
#include "board/Pin.h"
#include "board/Via.h"
#include "board/PolylineTrace.h"
#include "board/Layer.h"
#include "board/LayerStructure.h"
#include "board/Connectable.h"
#include "board/BasicBoard.h"
#include "rules/BoardRules.h"
#include "rules/Nets.h"
#include "rules/Net.h"
#include "rules/ViaRule.h"
#include "board/FixedState.h"
#include "geometry/planar/IntVector.h"
#include "tests/Validate.h"
#include "gui/Translation.h"

static const char* VERSION = "2.0.1";

static void register_fr_qt_types()
{
    qRegisterMetaType<QItemSelection>("QItemSelection");
}

static void print_help()
{
    std::cout << "FreeRouting version " << VERSION << "\n";
    std::cout << "command line options are:\n";
    std::cout << "-de  provide design file\n";
    std::cout << "-di  design folder used in file dialog\n";
    std::cout << "-l <lang>   language (en, de, fr, ja, ru, it, es, zh-CN, auto); default: LayoutEditor setting\n";
    std::cout << "-s   spectra session file is automatic saved on exit\n";
    std::cout << "-t   debug option\n";
    std::cout << "-white   white background\n";
    std::cout << "-h   this help\n";
    std::cout << "--selftest   run geometry/runtime checks\n";
    std::cout << "--dump <dsn>  load design and print board dump (headless)\n";
    std::cout << "--autoroute <dsn>  batch autoroute then write SES\n";
    std::cout << "--angle 90|45|any   snap angle for the GUI and --autoroute (default 45)\n";
    std::cout << "--no-postroute   skip the route optimizer after --autoroute\n";
    std::cout << "--ses <dsn>   export SES and exit\n";
    std::cout << "--manual-test <dsn>  headless route with push, pull tight, delete, via move, undo\n";
    std::cout << "--gui-smoke <dsn>  load GUI, exercise mouse/zoom/resize, exit\n";
    std::cout << "--repro-change-layer <dsn>  Manual Route, pin click, right-click change layer\n";
}

static int selftest()
{
    using java::math::BigInteger;
    int fail = 0;
    auto check = [&](bool c, const char* msg) {
        if (!c)
        {
            std::cerr << "FAIL " << msg << "\n";
            ++fail;
        }
    };
    check(BigInteger::valueOf(6).gcd(BigInteger::valueOf(9)).intValue() == 3, "gcd");
    check(BigInteger::valueOf(2).add(BigInteger::valueOf(3)).intValue() == 5, "add");
    check(BigInteger::valueOf(4).multiply(BigInteger::valueOf(5)).intValue() == 20, "mul");
    check(BigInteger::valueOf(11).divide(BigInteger::valueOf(3)).intValue() == 3, "div");
    check(BigInteger::ONE.equals(BigInteger::valueOf(1)), "one");

    java::util::Random r;
    r.setSeed(100);
    double a = r.nextDouble();
    r.setSeed(100);
    double b = r.nextDouble();
    check(a == b, "random seed");

    check(geometry::planar::Limits::CRIT_INT == 33554432, "crit_int");
    check(datastructures::BigIntAux::binaryGcd(12, 8) == 4, "binarygcd");
    auto* p = new geometry::planar::IntPoint(10, 20);
    check(p->x == 10 && p->y == 20, "intpoint");
    auto* p2 = new geometry::planar::IntPoint(10, 20);
    check(p->equals(static_cast<java::lang::Object*>(p2)), "intpoint_equals");
    auto* fp = p->to_float();
    check(fp != nullptr && fp->x == 10 && fp->y == 20, "floatpoint");

    auto* a_box = new geometry::planar::IntBox(0, 0, 100, 80);
    auto* b_box = new geometry::planar::IntBox(50, 40, 150, 120);
    check(a_box->intersects(b_box), "box_intersects");
    auto* isect = dynamic_cast<geometry::planar::IntBox*>(a_box->intersection(b_box));
    check(isect != nullptr && isect->ll->x == 50 && isect->ll->y == 40
              && isect->ur->x == 100 && isect->ur->y == 80,
          "box_intersection");
    auto* off = dynamic_cast<geometry::planar::IntBox*>(a_box->offset(10));
    check(off != nullptr && off->ll->x == -10 && off->ur->x == 110, "box_offset");
    auto* oct = a_box->to_IntOctagon();
    check(oct != nullptr && oct->intersects(a_box), "octagon");

    java::Array<geometry::planar::Point*> pts(3);
    pts[0] = new geometry::planar::IntPoint(0, 0);
    pts[1] = new geometry::planar::IntPoint(100, 0);
    pts[2] = new geometry::planar::IntPoint(100, 100);
    auto* pl = new geometry::planar::Polyline(pts);
    auto* off_sh = pl->offset_shape(10, 0);
    check(off_sh != nullptr && off_sh->bounding_box() != nullptr
              && off_sh->bounding_box()->width() >= 100,
          "polyline_offset");

    class TestStore : public datastructures::ShapeTree_Storable {
    public:
        geometry::planar::TileShape* sh = nullptr;
        int32_t tree_shape_count(datastructures::ShapeTree*) override { return 1; }
        geometry::planar::TileShape* get_tree_shape(datastructures::ShapeTree*, int32_t) override { return sh; }
        void set_search_tree_entries(java::Array<datastructures::ShapeTree_Leaf*>, datastructures::ShapeTree*) override {}
        int32_t compareTo(java::lang::Object* o) override { return java::lang::Object::compareTo(o); }
    };
    auto* tree = new datastructures::MinAreaTree(geometry::planar::OrthogonalBoundingDirections::INSTANCE);
    auto* store = new TestStore();
    store->sh = a_box;
    tree->datastructures::ShapeTree::insert(store);
    auto* ov = tree->overlaps(a_box);
    check(ov != nullptr && ov->size() >= 1, "minareatree_overlap");

    {
        struct Conn : virtual java::lang::Object {
            virtual void tag() = 0;
        };
        struct Draw : virtual java::lang::Object {};
        struct Search : virtual java::lang::Object {};
        struct Store : virtual java::lang::Object {};
        struct It : virtual java::lang::Object, public virtual Draw, public virtual Search, public virtual Store {
            int32_t id_no = 1;
            int32_t compareTo(java::lang::Object* o) override
            {
                if (auto* i = dynamic_cast<It*>(o))
                    return i->id_no - id_no;
                return 1;
            }
        };
        struct Tr : It, virtual Conn {
            void tag() override {}
        };
        Tr tr;
        tr.id_no = 7;
        It* ip = &tr;
        check(java::narrow<Conn*>(ip) != nullptr, "item_to_connectable");
        java::util::LinkedList<It*> list;
        java::util::TreeSet<It*> set;
        list.add(ip);
        It other;
        other.id_no = 8;
        list.add(&other);
        set.add(ip);
        list.removeAll(&set);
        check(list.size() == 1 && list.contains(&other) && !list.contains(ip),
              "removeAll_item_treeset");
        java::util::TreeMap<It*, int> tm;
        tm.put(ip, 1);
        tm.put(&other, 2);
        check(tm.get(ip) == 1 && tm.get(&other) == 2 && tm.size() == 2, "treemap_item_keys");
        tm.remove(ip);
        check(tm.get(ip) == 0 && tm.get(&other) == 2 && tm.size() == 1, "treemap_item_remove");

        struct Node : java::lang::Object {
            int level = 0;
        };
        It ka, kb, kc;
        ka.id_no = 10;
        kb.id_no = 11;
        kc.id_no = 12;
        Node n0, n1, n2;
        n0.level = 0;
        n1.level = 1;
        n2.level = 1;
        java::util::TreeMap<It*, Node*> redo;
        redo.put(&ka, &n0);
        redo.put(&kb, &n1);
        redo.put(&kc, &n2);
        auto* vit = redo.values()->iterator();
        while (vit->hasNext()) {
            auto* n = java::narrow<Node*>(vit->next());
            if (n && n->level > 0)
                vit->remove();
        }
        delete vit;
        check(redo.size() == 1 && redo.get(&ka) == &n0 && redo.get(&kb) == nullptr
                  && redo.get(&kc) == nullptr,
              "treemap_values_iterator_remove");
    }

    check(boardgraphics::ColorIntensityTable_ObjectNames::TRACES->toString()
              == QStringLiteral("TRACES"),
          "enum_toString");
    check(!boardgraphics::ColorIntensityTable_ObjectNames::VIAS->toString().contains(
              QLatin1String("Object@")),
          "enum_toString_not_object");

    if (fail == 0)
        std::cout << "selftest ok\n";
    else
        std::cout << "selftest failures: " << fail << "\n";
    return fail ? 1 : 0;
}

static QString arg_value(const QStringList& args, const QString& flag)
{
    int i = args.indexOf(flag);
    if (i >= 0 && i + 1 < args.size())
        return args[i + 1];
    return QString();
}

static QString json_str(const QString& s)
{
    QString o = QStringLiteral("\"");
    for (QChar c : s)
    {
        if (c == QLatin1Char('"'))
            o += QStringLiteral("\\\"");
        else if (c == QLatin1Char('\\'))
            o += QStringLiteral("\\\\");
        else if (c == QLatin1Char('\n'))
            o += QStringLiteral("\\n");
        else
            o += c;
    }
    return o + QLatin1Char('"');
}

static QString item_kind(board::Item* it)
{
    if (dynamic_cast<board::Pin*>(it))
        return QStringLiteral("board.Pin");
    if (dynamic_cast<board::Via*>(it))
        return QStringLiteral("board.Via");
    if (dynamic_cast<board::PolylineTrace*>(it))
        return QStringLiteral("board.PolylineTrace");
    if (dynamic_cast<board::BoardOutline*>(it))
        return QStringLiteral("board.BoardOutline");
    if (dynamic_cast<board::ComponentOutline*>(it))
        return QStringLiteral("board.ComponentOutline");
    if (dynamic_cast<board::ConductionArea*>(it))
        return QStringLiteral("board.ConductionArea");
    if (dynamic_cast<board::ViaObstacleArea*>(it))
        return QStringLiteral("board.ViaObstacleArea");
    if (dynamic_cast<board::ComponentObstacleArea*>(it))
        return QStringLiteral("board.ComponentObstacleArea");
    if (dynamic_cast<board::ObstacleArea*>(it))
        return QStringLiteral("board.ObstacleArea");
    return QStringLiteral("board.Item");
}

struct HeadlessSession {
    interactive::BoardHandling* hdlg = nullptr;
};

static HeadlessSession make_headless()
{
    HeadlessSession s;
    java::util::Locale locale = java::util::Locale::ENGLISH;
    auto* status = new java::swing::JLabel();
    auto* add = new java::swing::JLabel();
    auto* layer = new java::swing::JLabel();
    auto* mouse = new java::swing::JLabel();
    auto* sm = new interactive::ScreenMessages(status, add, layer, mouse, locale);
    auto* panel = new gui::BoardPanel();
    panel->setPreferredSize(QSize(1200, 900));
    panel->resize(1200, 900);
    panel->screen_messages = sm;
    auto* frame = new gui::BoardFrame();
    panel->board_frame = frame;
    frame->board_panel = panel;
    frame->screen_messages = sm;
    s.hdlg = new interactive::BoardHandling(panel, locale);
    panel->board_handling = s.hdlg;
    return s;
}

static int load_dsn(interactive::BoardHandling* hdlg, const QString& path, board::TestLevel* test_level = board::TestLevel::RELEASE_VERSION)
{
    java::io::FileInputStream* in = nullptr;
    try
    {
        in = new java::io::FileInputStream(path);
    }
    catch (const java::io::IOException& e)
    {
        std::cerr << "cannot open " << path.toStdString() << ": " << e.what() << "\n";
        return 1;
    }
    if (java::fr_eq(in, nullptr))
    {
        std::cerr << "cannot open " << path.toStdString() << "\n";
        return 1;
    }
    designformats::specctra::DsnFile_ReadResult* result = nullptr;
    try
    {
        result = hdlg->import_design(in, new board::BoardObserverAdaptor(),
                                     new board::ItemIdNoGenerator(),
                                     test_level);
    }
    catch (java::lang::Error* e)
    {
        std::cerr << "import Error*: " << (e ? e->getMessage().toStdString() : "?") << "\n";
        return 1;
    }
    if (result != designformats::specctra::DsnFile_ReadResult::OK)
    {
        std::cerr << "DsnFile.read failed for " << path.toStdString() << "\n";
        return 1;
    }
    if (!hdlg->get_routing_board())
    {
        std::cerr << "no routing board after DSN import\n";
        return 1;
    }
    return 0;
}

static QString ses_path_for(const QString& dsn)
{
    QFileInfo fi(dsn);
    return fi.dir().filePath(fi.completeBaseName() + QStringLiteral(".ses"));
}

static int write_ses(interactive::BoardHandling* hdlg, const QString& dsn, const QString& out_path)
{
    try
    {
        auto* out = new java::io::FileOutputStream(out_path);
        QString name = QFileInfo(dsn).fileName();
        if (!hdlg->export_specctra_session_file(name, out))
        {
            std::cerr << "SES export failed\n";
            return 1;
        }
        out->close();
    }
    catch (const java::io::IOException& e)
    {
        std::cerr << "cannot write " << out_path.toStdString() << ": " << e.what() << "\n";
        return 1;
    }
    std::cerr << "wrote " << out_path.toStdString() << "\n";
    return 0;
}

static int dump_board(interactive::BoardHandling* hdlg, const QString& dsn)
{
    board::RoutingBoard* board = hdlg->get_routing_board();
    std::vector<board::Item*> items;
    if (auto* col = board->get_items())
    {
        auto* it = col->iterator();
        while (it && it->hasNext())
        {
            board::Item* item = it->next();
            if (item)
                items.push_back(item);
        }
        delete it;
    }
    std::sort(items.begin(), items.end(), [](board::Item* a, board::Item* b) {
        return a->get_id_no() < b->get_id_no();
    });

    int32_t cv = 0;
    for (auto* item : items)
    {
        auto* vs = item->clearance_violations();
        if (vs)
            cv += vs->size();
    }

    int32_t incomplete = 0;
    if (auto* rn = hdlg->get_ratsnest())
        incomplete = rn->incomplete_count();

    bool valid = tests::Validate::check(QStringLiteral("dump"), board);
    int32_t net_count = 0;
    if (board->rules && board->rules->nets && board->rules->nets->net_arr)
        net_count = board->rules->nets->net_arr->size();

    int32_t keepouts = 0;
    for (auto* item : items)
    {
        if (dynamic_cast<board::ViaObstacleArea*>(item) || dynamic_cast<board::ComponentObstacleArea*>(item))
            continue;
        if (dynamic_cast<board::ObstacleArea*>(item))
            ++keepouts;
    }

    std::cout << "{\n";
    std::cout << "  \"dsn\": " << json_str(dsn).toStdString() << ",\n";
    std::cout << "  \"item_count\": " << items.size() << ",\n";
    std::cout << "  \"net_count\": " << net_count << ",\n";
    std::cout << "  \"layer_count\": " << board->get_layer_count() << ",\n";
    std::cout << "  \"keepout_count\": " << keepouts << ",\n";
    std::cout << "  \"incompletes\": " << incomplete << ",\n";
    std::cout << "  \"clearance_violations\": " << cv << ",\n";
    std::cout << "  \"validate_ok\": " << (valid ? "true" : "false") << ",\n";
    std::cout << "  \"classes\": [";
    if (board->rules && board->rules->net_classes)
    {
        bool first_class = true;
        for (int32_t ci = 0; ci < board->rules->net_classes->count(); ++ci)
        {
            rules::NetClass* nc = board->rules->net_classes->get(ci);
            if (!nc)
                continue;
            int32_t width = nc->get_trace_half_width(0) * 2;
            if (!first_class)
                std::cout << ",";
            first_class = false;
            std::cout << "{\"name\": " << json_str(nc->get_name()).toStdString()
                      << ", \"width\": " << width << "}";
        }
    }
    std::cout << "],\n";
    std::cout << "  \"items\": [\n";
    for (size_t i = 0; i < items.size(); ++i)
    {
        board::Item* item = items[i];
        QString nets;
        for (int32_t n = 0; n < item->net_no_arr.length; ++n)
        {
            if (n)
                nets += QLatin1Char(',');
            nets += QString::number(item->net_no_arr[n]);
        }
        auto* bb = item->bounding_box();
        std::cout << "    {\"id\": " << item->get_id_no()
                  << ", \"type\": " << json_str(item_kind(item)).toStdString()
                  << ", \"nets\": [" << nets.toStdString() << "]";
        if (bb && bb->ll && bb->ur)
        {
            std::cout << ", \"bbox\": [" << bb->ll->x << "," << bb->ll->y << ","
                      << bb->ur->x << "," << bb->ur->y << "]";
        }
        if (auto* pin = dynamic_cast<board::Pin*>(item))
        {
            if (auto* c = dynamic_cast<geometry::planar::IntPoint*>(pin->get_center()))
                std::cout << ", \"xy\": [" << c->x << "," << c->y << "]";
        }
        std::cout << "}";
        if (i + 1 < items.size())
            std::cout << ",";
        std::cout << "\n";
    }
    std::cout << "  ]\n}\n";
    return 0;
}

static int32_t count_clearance_violations(board::RoutingBoard* board)
{
    int32_t cv = 0;
    auto* items = board->get_items();
    auto* it = items->iterator();
    while (it->hasNext()) {
        board::Item* item = it->next();
        auto* vs = item != nullptr ? item->clearance_violations() : nullptr;
        if (vs != nullptr)
            cv += vs->size();
        delete vs;
    }
    delete it;
    delete items;
    return cv;
}

template <class T>
static std::vector<T*> board_items_of(board::RoutingBoard* board)
{
    std::vector<T*> out;
    auto* items = board->get_items();
    auto* it = items->iterator();
    while (it->hasNext()) {
        board::Item* item = it->next();
        if (auto* typed = dynamic_cast<T*>(item))
            out.push_back(typed);
    }
    delete it;
    delete items;
    return out;
}

// Route with push, pull tight, delete with pull tight, via insert and move, undo:
// the board operations behind the interactive menu functions.
static int run_manual_test(interactive::BoardHandling* hdlg)
{
    board::RoutingBoard* board = hdlg->get_routing_board();
    int fail = 0;
    // some fixtures ship with violations between fixed items
    const int32_t cv_start = count_clearance_violations(board);
    auto step_ok = [&](const char* step, bool ok, const std::string& detail) {
        const int32_t cv = count_clearance_violations(board);
        const bool valid = tests::Validate::check(QString::fromLatin1(step), board);
        const bool pass = ok && cv <= cv_start && valid;
        std::cout << "manual " << step << (pass ? " ok" : " FAILED") << " " << detail << " clearance " << cv
                  << " valid " << (valid ? 1 : 0) << "\n";
        if (!pass)
            ++fail;
    };
    const int32_t accuracy = hdlg->settings->trace_pull_tight_accuracy;
    const int32_t tidy = java::lang::Integer::MAX_VALUE;
    const std::size_t items_before = board_items_of<board::Item>(board).size();
    board->generate_snapshot();

    struct Routed {
        int32_t net;
        int32_t layer;
        geometry::planar::IntPoint* corner;
    };
    std::vector<Routed> routed;
    int32_t tried = 0;
    const int32_t max_net = board->rules->nets->max_net_no();
    for (int32_t net_no = 1; net_no <= max_net && routed.size() < 12 && tried < 80; ++net_no) {
        rules::Net* net = board->rules->nets->get(net_no);
        if (net == nullptr || net->contains_plane())
            continue;
        auto* pins = net->get_pins();
        std::vector<board::Pin*> pv;
        for (auto* p : java::iterate(pins))
            pv.push_back(p);
        delete pins;
        if (pv.size() < 2)
            continue;
        board::Pin* p = pv[0];
        board::Pin* q = pv[1];
        const int32_t layer = std::max(p->first_layer(), q->first_layer());
        if (layer > std::min(p->last_layer(), q->last_layer()))
            continue;
        auto* a = dynamic_cast<geometry::planar::IntPoint*>(p->get_center());
        auto* b = dynamic_cast<geometry::planar::IntPoint*>(q->get_center());
        if (a == nullptr || b == nullptr || a->equals(b))
            continue;
        ++tried;
        const int32_t half = board->rules->get_trace_half_width(net_no, layer);
        const int32_t cl = net->get_class()->get_trace_clearance_class();
        java::Array<int32_t> nets(1);
        nets[0] = net_no;
        auto* mid = new geometry::planar::IntPoint(b->x, a->y);
        geometry::planar::Point* reached = board->insert_forced_trace_segment(a, mid, half, layer, nets, cl, 20, 8, 5, tidy, accuracy, true, nullptr);
        if (reached == nullptr || !reached->equals(mid))
            continue;
        if (!mid->equals(b))
            reached = board->insert_forced_trace_segment(mid, b, half, layer, nets, cl, 20, 8, 5, tidy, accuracy, true, nullptr);
        if (reached != nullptr && reached->equals(b))
            routed.push_back({ net_no, layer, mid->equals(b) ? new geometry::planar::IntPoint((a->x + b->x) / 2, (a->y + b->y) / 2) : mid });
    }
    step_ok("route_push", !routed.empty(), "routed " + std::to_string(routed.size()) + "/" + std::to_string(tried));

    board->mark_all_changed_area();
    board->opt_changed_area(java::Array<int32_t>(0), nullptr, accuracy, nullptr, nullptr, 0);
    step_ok("pull_tight", true, "traces " + std::to_string(board_items_of<board::PolylineTrace>(board).size()));

    bool removed = false;
    for (board::PolylineTrace* trace : board_items_of<board::PolylineTrace>(board)) {
        if (trace->net_count() != 1 || trace->get_fixed_state() != board::FixedState::UNFIXED)
            continue;
        const int32_t id = trace->get_id_no();
        auto* list = new java::util::LinkedList<board::Item*>();
        list->add(trace);
        board->remove_items_and_pull_tight(list, tidy, accuracy, false);
        delete list;
        removed = true;
        for (board::Item* item : board_items_of<board::Item>(board))
            removed = removed && item->get_id_no() != id;
        break;
    }
    step_ok("delete_pull_tight", removed, "");

    board::Via* via = nullptr;
    const std::size_t vias_before = board_items_of<board::Via>(board).size();
    for (const Routed& r : routed) {
        rules::Net* net = board->rules->nets->get(r.net);
        rules::ViaRule* via_rule = net->get_class()->get_via_rule();
        if (via_rule == nullptr || via_rule->via_count() == 0)
            continue;
        java::Array<int32_t> nets(1);
        nets[0] = r.net;
        java::Array<int32_t> half_arr(board->get_layer_count());
        for (int32_t l = 0; l < board->get_layer_count(); ++l)
            half_arr[l] = board->rules->get_trace_half_width(r.net, l);
        if (!board->forced_via(via_rule->get_via(0), r.corner, nets, net->get_class()->get_trace_clearance_class(), half_arr, 20, 8, tidy, accuracy, 0))
            continue;
        for (board::Via* v : board_items_of<board::Via>(board)) {
            if (v->get_center()->equals(r.corner))
                via = v;
        }
        if (via != nullptr)
            break;
    }
    step_ok("via_insert", via != nullptr && board_items_of<board::Via>(board).size() == vias_before + 1, "");

    bool moved = false;
    std::string move_detail;
    if (via != nullptr) {
        auto* start = dynamic_cast<geometry::planar::IntPoint*>(via->get_center());
        const int32_t x0 = start != nullptr ? start->x : 0;
        const int32_t y0 = start != nullptr ? start->y : 0;
        const int32_t dist = 4 * board->get_min_trace_half_width();
        const int32_t dirs[4][2] = { { 1, 0 }, { 0, 1 }, { -1, 0 }, { 0, -1 } };
        for (const auto& d : dirs) {
            if (!board->move_drill_item(via, new geometry::planar::IntVector(d[0] * dist, d[1] * dist), 20, 8, tidy, accuracy, 0))
                continue;
            auto* now = dynamic_cast<geometry::planar::IntPoint*>(via->get_center());
            moved = now != nullptr && (now->x != x0 || now->y != y0);
            move_detail = "by " + std::to_string(d[0] * dist) + "," + std::to_string(d[1] * dist);
            break;
        }
    }
    step_ok("via_move", moved, move_detail);

    board->undo(nullptr);
    const std::size_t items_after = board_items_of<board::Item>(board).size();
    step_ok("undo", items_after == items_before, "items " + std::to_string(items_after) + "/" + std::to_string(items_before));

    std::cout << (fail == 0 ? "manual-test ok\n" : "manual-test failures\n");
    return fail == 0 ? 0 : 1;
}

static QtMessageHandler previous_message_handler = nullptr;

// Qt 5 on Wayland loads the ibus input context while QApplication builds its event
// dispatcher; its QFileSystemWatcher then warns about QSocketNotifier. Harmless.
static void message_handler(QtMsgType type, const QMessageLogContext& context, const QString& msg)
{
    if (type == QtWarningMsg && msg.startsWith(QLatin1String("QSocketNotifier: Can only be used with threads started with QThread")))
        return;
    if (previous_message_handler != nullptr)
        previous_message_handler(type, context, msg);
}

static void install_message_handler()
{
    previous_message_handler = qInstallMessageHandler(message_handler);
}

static int run_headless(const QStringList& args)
{
    int qargc = 1;
    char qarg0[] = "freeRouting";
    char* qargv[] = { qarg0, nullptr };
    QCoreApplication::setAttribute(Qt::AA_DontUseNativeMenuBar);
    install_message_handler();
    QApplication app(qargc, qargv);
    app.setApplicationName(QStringLiteral("FreeRouting"));
    app.setApplicationVersion(QString::fromLatin1(VERSION));
    register_fr_qt_types();

    QString dump_dsn = arg_value(args, QStringLiteral("--dump"));
    QString ses_dsn = arg_value(args, QStringLiteral("--ses"));
    QString ar_dsn = arg_value(args, QStringLiteral("--autoroute"));
    QString manual_dsn = arg_value(args, QStringLiteral("--manual-test"));
    QString dsn = dump_dsn;
    if (dsn.isEmpty())
        dsn = ses_dsn;
    if (dsn.isEmpty())
        dsn = ar_dsn;
    if (dsn.isEmpty())
        dsn = manual_dsn;
    if (dsn.isEmpty())
        return 2;

    HeadlessSession s = make_headless();
    board::TestLevel* test_level = board::TestLevel::RELEASE_VERSION;
    if (args.contains(QStringLiteral("-t")) || args.contains(QStringLiteral("-debug")))
        test_level = board::TestLevel::CRITICAL_DEBUGGING_OUTPUT;
    if (load_dsn(s.hdlg, dsn, test_level) != 0)
        return 1;

    if (!manual_dsn.isEmpty())
        return run_manual_test(s.hdlg);
    if (!dump_dsn.isEmpty())
    {
        if (dump_board(s.hdlg, dsn) != 0)
            return 1;
    }
    if (!ar_dsn.isEmpty())
    {
        QString angle = arg_value(args, QStringLiteral("--angle"));
        if (!angle.isEmpty())
        {
            board::AngleRestriction* restriction = nullptr;
            if (angle == QLatin1String("90"))
                restriction = board::AngleRestriction::NINETY_DEGREE;
            else if (angle == QLatin1String("45"))
                restriction = board::AngleRestriction::FORTYFIVE_DEGREE;
            else if (angle == QLatin1String("any"))
                restriction = board::AngleRestriction::NONE;
            else
            {
                std::cerr << "--angle expects 90, 45, or any\n";
                return 2;
            }
            s.hdlg->set_current_snap_angle(restriction);
            std::cerr << "angle " << angle.toStdString() << "\n";
        }
        if (args.contains(QStringLiteral("--no-postroute")))
            s.hdlg->settings->autoroute_settings->set_with_postroute(false);
        auto* th = interactive::InteractiveActionThread::get_batch_autorouter_instance(s.hdlg);
        if (test_level != board::TestLevel::RELEASE_VERSION)
            std::cerr << "autoroute start\n" << std::flush;
        int ar_rc = 0;
        try
        {
            th->thread_action();
        }
        catch (const java::lang::Throwable& t)
        {
            std::cerr << "autoroute Throwable: " << t.getMessage().toStdString() << "\n";
            ar_rc = 1;
        }
        catch (java::lang::Throwable* t)
        {
            std::cerr << "autoroute Throwable*: "
                      << (t ? t->getMessage().toStdString() : "?") << "\n";
            ar_rc = 1;
        }
        catch (const std::exception& e)
        {
            std::cerr << "autoroute std::exception: " << e.what() << "\n";
            ar_rc = 1;
        }
        catch (...)
        {
            std::cerr << "autoroute unknown exception\n";
            ar_rc = 1;
        }
        if (ar_rc != 0)
            return ar_rc;
        std::cerr << "autoroute done\n" << std::flush;
        QString out = ses_path_for(ar_dsn);
        if (write_ses(s.hdlg, ar_dsn, out) != 0)
            return 1;
        if (auto* rn = s.hdlg->get_ratsnest())
            std::cerr << "incompletes " << rn->incomplete_count() << "\n";
        int32_t cv = 0;
        auto* items = s.hdlg->get_routing_board()->get_items();
        if (items)
        {
            auto* it = items->iterator();
            while (it && it->hasNext())
            {
                board::Item* item = it->next();
                auto* vs = item ? item->clearance_violations() : nullptr;
                if (!vs)
                    continue;
                cv += vs->size();
                if (!args.contains(QStringLiteral("--clearance-list")))
                    continue;
                auto* vit = vs->iterator();
                while (vit && vit->hasNext())
                {
                    board::ClearanceViolation* v = vit->next();
                    auto net_of = [](board::Item* x) {
                        return x && x->net_no_arr.length > 0 ? x->net_no_arr[0] : 0;
                    };
                    std::cerr << "violation layer " << v->layer << " "
                              << item_kind(v->first_item).toStdString() << " net " << net_of(v->first_item) << " / "
                              << item_kind(v->second_item).toStdString() << " net " << net_of(v->second_item);
                    auto* bb = v->shape ? v->shape->bounding_box() : nullptr;
                    if (bb && bb->ll && bb->ur)
                        std::cerr << " box " << bb->ll->x << "," << bb->ll->y << " " << bb->ur->x << "," << bb->ur->y;
                    std::cerr << "\n";
                }
                delete vit;
            }
            delete it;
        }
        std::cerr << "clearance " << cv << "\n";
    }
    else if (!ses_dsn.isEmpty())
    {
        if (write_ses(s.hdlg, ses_dsn, ses_path_for(ses_dsn)) != 0)
            return 1;
    }
    return 0;
}

#ifdef FR_HAS_GUI_MAIN
static void send_mouse(QWidget* w, QEvent::Type t, const QPoint& local, Qt::MouseButton b, Qt::MouseButtons bs)
{
    const QPoint glob = w->mapToGlobal(local);
    QMouseEvent e(t, QPointF(local), glob, b, bs, Qt::NoModifier);
    QApplication::sendEvent(w, &e);
    QApplication::processEvents();
}

static void send_wheel(QWidget* w, const QPoint& local, int angle_y)
{
    const QPoint glob = w->mapToGlobal(local);
    QWheelEvent e(QPointF(local), glob, QPoint(), QPoint(0, angle_y),
                  Qt::NoButton, Qt::NoModifier, Qt::ScrollUpdate, false);
    QApplication::sendEvent(w, &e);
    QApplication::processEvents();
}

static void flush_gui(int n = 20)
{
    for (int i = 0; i < n; ++i)
        QApplication::processEvents();
}

static const char* interactive_state_name(interactive::InteractiveState* s)
{
    if (!s)
        return "null";
    if (dynamic_cast<interactive::DynamicRouteState*>(s))
        return "DynamicRouteState";
    if (dynamic_cast<interactive::StitchRouteState*>(s))
        return "StitchRouteState";
    if (dynamic_cast<interactive::RouteMenuState*>(s))
        return "RouteMenuState";
    if (dynamic_cast<interactive::RouteState*>(s))
        return "RouteState";
    if (dynamic_cast<interactive::SelectMenuState*>(s))
        return "SelectMenuState";
    return typeid(*s).name();
}

static QPoint widget_center(QWidget* w)
{
    return QPoint(qMax(1, w->width() / 2), qMax(1, w->height() / 2));
}

static void click_widget(QWidget* w, const QPoint& local, Qt::MouseButton b)
{
    send_mouse(w, QEvent::MouseButtonPress, local, b, b);
    send_mouse(w, QEvent::MouseButtonRelease, local, b, Qt::NoButton);
}

static int run_repro_change_layer(const QString& dsn)
{
    if (dsn.isEmpty() || !QFileInfo::exists(dsn)) {
        std::cerr << "repro-change-layer: missing dsn\n";
        return 1;
    }
    std::cerr << "repro-change-layer: dsn " << dsn.toStdString()
              << " platform " << QGuiApplication::platformName().toStdString() << "\n";
    gui::DesignFile* designFile = gui::DesignFile::get_instance(dsn);
    if (!designFile) {
        std::cerr << "repro-change-layer: cannot open " << dsn.toStdString() << "\n";
        return 1;
    }
    gui::BoardFrame* frame = gui::MainApplication::createBoardFrame(
        designFile, false, false, java::util::Locale::ENGLISH, false);
    if (!frame || !frame->board_panel) {
        std::cerr << "repro-change-layer: createBoardFrame failed\n";
        return 1;
    }
    frame->show();
    flush_gui();
    frame->zoom_all();
    flush_gui();
    gui::BoardPanel* panel = frame->board_panel;
    std::cerr << "repro-change-layer: panel size=" << panel->width() << "x" << panel->height()
              << "\n";
    interactive::BoardHandling* hdlg = panel->board_handling;
    gui::BoardToolbar* tb = frame->toolbar_panel;
    if (!tb || !tb->routingButton) {
        std::cerr << "repro-change-layer: routing toolbar button missing\n";
        return 1;
    }
    if (tb->routingButton->width() < 1 || tb->routingButton->height() < 1) {
        std::cerr << "repro-change-layer: routing button has no size "
                  << tb->routingButton->width() << "x" << tb->routingButton->height() << "\n";
        return 1;
    }
    std::cerr << "repro-change-layer: click Manual Route  state="
              << interactive_state_name(hdlg->get_interactive_state()) << "\n";
    click_widget(tb->routingButton, widget_center(tb->routingButton), Qt::LeftButton);
    flush_gui();
    if (!dynamic_cast<interactive::RouteMenuState*>(hdlg->get_interactive_state())) {
        std::cerr << "repro-change-layer: Manual Route did not enter RouteMenuState, state="
                  << interactive_state_name(hdlg->get_interactive_state()) << "\n";
        return 1;
    }

    board::Pin* pin = nullptr;
    if (auto* items = hdlg->get_routing_board()->get_items()) {
        auto* it = items->iterator();
        while (it && it->hasNext()) {
            board::Item* item = it->next();
            auto* p = dynamic_cast<board::Pin*>(item);
            if (!p)
                continue;
            if (!pin)
                pin = p;
            if (p->first_layer() == p->last_layer()) {
                pin = p;
                break;
            }
        }
        delete it;
    }
    if (!pin || !pin->get_center() || !hdlg->graphics_context
        || !hdlg->graphics_context->coordinate_transform) {
        std::cerr << "repro-change-layer: no pin with center\n";
        return 1;
    }
    auto* fp = pin->get_center()->to_float();
    java::awt::geom::Point2D* scr =
        hdlg->graphics_context->coordinate_transform->board_to_screen(fp);
    if (!scr) {
        std::cerr << "repro-change-layer: pin has no screen coordinate\n";
        return 1;
    }
    const QPoint pin_pt(qRound(scr->x()), qRound(scr->y()));
    const int pin_layer = pin->first_layer();
    std::cerr << "repro-change-layer: left-click pin at " << pin_pt.x() << "," << pin_pt.y()
              << " pin_layer=" << pin_layer
              << " settings_layer=" << hdlg->settings->get_layer() << "\n";
    click_widget(panel, pin_pt, Qt::LeftButton);
    flush_gui();
    auto* after = hdlg->get_interactive_state();
    auto* route_state = dynamic_cast<interactive::RouteState*>(after);
    if (!route_state || dynamic_cast<interactive::RouteMenuState*>(after)) {
        std::cerr << "repro-change-layer: pin click did not start routing, state="
                  << interactive_state_name(after) << "\n";
        return 1;
    }
    std::cerr << "repro-change-layer: after pin  state=" << interactive_state_name(after)
              << " route=" << static_cast<const void*>(route_state->route)
              << " smd=" << (pin->first_layer() == pin->last_layer() ? 1 : 0)
              << " pin_layers=" << pin->first_layer() << ".." << pin->last_layer() << "\n";
    if (!route_state->route) {
        std::cerr << "repro-change-layer: RouteState.route is null\n";
        return 1;
    }
    const QPoint menu_pt = [&]() {
        auto* pc = pin->get_center()->to_float();
        auto* away = new geometry::planar::FloatPoint(pc->x + 800, pc->y + 200);
        java::awt::geom::Point2D* mscr =
            hdlg->graphics_context->coordinate_transform->board_to_screen(away);
        if (mscr)
            return QPoint(qRound(mscr->x()), qRound(mscr->y()));
        return pin_pt + QPoint(180, 40);
    }();
    std::cerr << "repro-change-layer: move toward menu " << menu_pt.x() << "," << menu_pt.y() << "\n";
    send_mouse(panel, QEvent::MouseMove, menu_pt, Qt::NoButton, Qt::NoButton);
    flush_gui();
    after = hdlg->get_interactive_state();
    route_state = dynamic_cast<interactive::RouteState*>(after);
    std::cerr << "repro-change-layer: after move  state=" << interactive_state_name(after)
              << " route=" << static_cast<const void*>(route_state ? route_state->route : nullptr)
              << "\n";
    if (!route_state || !route_state->route) {
        std::cerr << "repro-change-layer: route lost after mouse move\n";
        return 1;
    }
    if (hdlg->settings)
        hdlg->settings->set_via_snap_to_smd_center(false);
    route_state->route->via_snap_to_smd_center = false;
    if (auto* last = route_state->route->get_last_corner()) {
        auto* lf = last->to_float();
        auto* pf = pin->get_center() ? pin->get_center()->to_float() : nullptr;
        std::cerr << "repro-change-layer: last_corner="
                  << (lf ? lf->x : 0) << "," << (lf ? lf->y : 0)
                  << " pin_center=" << (pf ? pf->x : 0) << "," << (pf ? pf->y : 0)
                  << " snap=" << (int)route_state->route->via_snap_to_smd_center
                  << " via_rule=" << static_cast<const void*>(route_state->route->via_rule)
                  << "\n";
    }

    java::swing::JPopupMenu* expected_popup = hdlg->get_current_popup_menu();
    std::cerr << "repro-change-layer: right-click at " << menu_pt.x() << "," << menu_pt.y()
              << " expected_popup=" << static_cast<const void*>(expected_popup)
              << " visible=" << (expected_popup && expected_popup->isVisible() ? 1 : 0) << "\n";
    click_widget(panel, menu_pt, Qt::RightButton);
    flush_gui();
    java::swing::JPopupMenu* popup = hdlg->get_current_popup_menu();
    if (!popup) {
        std::cerr << "repro-change-layer: no popup menu after right-click, state="
                  << interactive_state_name(hdlg->get_interactive_state()) << "\n";
        return 1;
    }
    if (!popup->isVisible()) {
        std::cerr << "repro-change-layer: popup not visible after right-click (title='"
                  << popup->title().toStdString() << "')\n";
        return 1;
    }
    if (!panel->right_button_click_location) {
        std::cerr << "repro-change-layer: right_button_click_location not set\n";
        return 1;
    }
    std::cerr << "repro-change-layer: popup visible size="
              << popup->width() << "x" << popup->height()
              << " actions=" << popup->actions().size() << "\n";

    QAction* change_layer_act = nullptr;
    QMenu* layer_menu = nullptr;
    for (QAction* a : popup->actions()) {
        QMenu* sub = a ? a->menu() : nullptr;
        if (!sub)
            continue;
        const QString t = sub->title().isEmpty() ? a->text() : sub->title();
        if (!t.contains(QLatin1String("layer"), Qt::CaseInsensitive)
            && !t.contains(QString::fromUtf8("Lage")))
            continue;
        change_layer_act = a;
        layer_menu = sub;
        break;
    }
    if (!change_layer_act || !layer_menu) {
        std::cerr << "repro-change-layer: change-layer submenu missing\n";
        return 1;
    }
    std::cerr << "repro-change-layer: open submenu '" << layer_menu->title().toStdString()
              << "' via actionGeometry\n";
    {
        const QRect r = popup->actionGeometry(change_layer_act);
        if (!r.isValid() || r.width() < 1 || r.height() < 1) {
            std::cerr << "repro-change-layer: change-layer actionGeometry invalid "
                      << r.x() << "," << r.y() << " " << r.width() << "x" << r.height() << "\n";
            return 1;
        }
        send_mouse(popup, QEvent::MouseMove, r.center(), Qt::NoButton, Qt::NoButton);
        popup->setActiveAction(change_layer_act);
        flush_gui();
    }
    if (!layer_menu->isVisible()) {
        std::cerr << "repro-change-layer: change-layer submenu not visible after hover\n";
        return 1;
    }
    std::cerr << "repro-change-layer: submenu visible size="
              << layer_menu->width() << "x" << layer_menu->height()
              << " actions=" << layer_menu->actions().size() << "\n";

    QAction* layer_act = nullptr;
    int32_t chosen_layer = -1;
    for (QAction* a : layer_menu->actions()) {
        if (!a || !a->isEnabled())
            continue;
        auto* item = dynamic_cast<gui::PopupMenuChangeLayer_LayermenuItem*>(a);
        if (item)
            chosen_layer = item->layer_no;
        layer_act = a;
        break;
    }
    if (!layer_act) {
        std::cerr << "repro-change-layer: no enabled layer action\n";
        return 1;
    }
    const QRect layer_r = layer_menu->actionGeometry(layer_act);
    if (!layer_r.isValid() || layer_r.width() < 1 || layer_r.height() < 1) {
        std::cerr << "repro-change-layer: layer actionGeometry invalid\n";
        return 1;
    }
    std::cerr << "repro-change-layer: click layer action '" << layer_act->text().toStdString()
              << "' layer_no=" << chosen_layer
              << " geom=" << layer_r.x() << "," << layer_r.y()
              << " " << layer_r.width() << "x" << layer_r.height()
              << " state=" << interactive_state_name(hdlg->get_interactive_state())
              << " route=" << static_cast<const void*>(
                     dynamic_cast<interactive::RouteState*>(hdlg->get_interactive_state())
                         ? dynamic_cast<interactive::RouteState*>(hdlg->get_interactive_state())->route
                         : nullptr)
              << "\n";
    bool action_fired = false;
    QObject::connect(layer_act, &QAction::triggered, layer_act, [&action_fired](bool) {
        action_fired = true;
    });
    const QPoint layer_global = layer_menu->mapToGlobal(layer_r.center());
    std::cerr << "repro-change-layer: cursor to layer item global "
              << layer_global.x() << "," << layer_global.y() << "\n";
    QCursor::setPos(layer_global);
    flush_gui();
    QWidget* hit = QApplication::widgetAt(layer_global);
    std::cerr << "repro-change-layer: widgetAt="
              << (hit ? hit->metaObject()->className() : "null")
              << " visible=" << (hit && hit->isVisible() ? 1 : 0) << "\n";
    if (hit) {
        click_widget(hit, hit->mapFromGlobal(layer_global), Qt::LeftButton);
    } else {
        send_mouse(layer_menu, QEvent::MouseMove, layer_r.center(), Qt::NoButton, Qt::NoButton);
        click_widget(layer_menu, layer_r.center(), Qt::LeftButton);
    }
    if (QWindow* wh = layer_menu->windowHandle()) {
        const QPoint l = layer_r.center();
        QMouseEvent e1(QEvent::MouseButtonPress, QPointF(l), layer_global,
                         Qt::LeftButton, Qt::LeftButton, Qt::NoModifier);
        QMouseEvent e2(QEvent::MouseButtonRelease, QPointF(l), layer_global,
                         Qt::LeftButton, Qt::NoButton, Qt::NoModifier);
        QApplication::sendEvent(wh, &e1);
        QApplication::processEvents();
        QApplication::sendEvent(wh, &e2);
        QApplication::processEvents();
    }
    panel->QWidget::repaint();
    flush_gui(50);
    after = hdlg->get_interactive_state();
    route_state = dynamic_cast<interactive::RouteState*>(after);
    QString status;
    if (hdlg->screen_messages && hdlg->screen_messages->status_field)
        status = hdlg->screen_messages->status_field->text();
    std::cerr << "repro-change-layer: after layer click  state="
              << interactive_state_name(after)
              << " route=" << static_cast<const void*>(route_state ? route_state->route : nullptr)
              << " settings_layer=" << (hdlg->settings ? hdlg->settings->get_layer() : -1)
              << " action_fired=" << (action_fired ? 1 : 0)
              << " status='" << status.toStdString() << "'\n";
    std::cout << "repro-change-layer ok\n";
    return 0;
}

static int run_gui_smoke(const QString& dsn)
{
    if (dsn.isEmpty() || !QFileInfo::exists(dsn)) {
        std::cerr << "gui-smoke: missing dsn\n";
        return 1;
    }
    gui::DesignFile* designFile = gui::DesignFile::get_instance(dsn);
    if (!designFile) {
        std::cerr << "gui-smoke: cannot open " << dsn.toStdString() << "\n";
        return 1;
    }
    gui::BoardFrame* frame = gui::MainApplication::createBoardFrame(
        designFile, false, false, java::util::Locale::ENGLISH, false);
    if (!frame || !frame->board_panel) {
        std::cerr << "gui-smoke: createBoardFrame failed\n";
        return 1;
    }
    frame->show();
    QApplication::processEvents();
    {
        QMenuBar* mb = frame->menuBar();
        if (!mb || !mb->isVisible()) {
            std::cerr << "gui-smoke: menubar not visible\n";
            return 1;
        }
        for (QWidget* w : QApplication::allWidgets()) {
            auto* menu = qobject_cast<QMenu*>(w);
            if (!menu || !menu->isVisible())
                continue;
            std::cerr << "gui-smoke: QMenu '" << menu->title().toStdString()
                      << "' is visible after show (covers menubar/toolbar)\n";
            return 1;
        }
    }
    gui::BoardPanel* panel = frame->board_panel;
    interactive::BoardHandling* hdlg = panel->board_handling;
    auto wait_action_thread_stop = [&]() {
        if (!hdlg || !hdlg->interactive_action_thread)
            return;
        hdlg->interactive_action_thread->request_stop();
        for (int i = 0; i < 250; ++i) {
            QApplication::processEvents();
            const bool alive = hdlg->interactive_action_thread
                && hdlg->interactive_action_thread->isAlive();
            if (!alive && !hdlg->is_board_read_only())
                break;
            QThread::msleep(20);
        }
    };
    {
        gui::BoardToolbar* tb = frame->toolbar_panel;
        QAction* autoroute_item = nullptr;
        if (frame->menuBar()) {
            for (QAction* top : frame->menuBar()->actions()) {
                QMenu* m = top ? top->menu() : nullptr;
                if (!m)
                    continue;
                for (QAction* it : m->actions()) {
                    if (it && it->text().contains(QLatin1String("Autorout"), Qt::CaseInsensitive)) {
                        autoroute_item = it;
                        break;
                    }
                }
                if (autoroute_item)
                    break;
            }
        }
        if (!autoroute_item) {
            std::cerr << "gui-smoke: Routing/Autorouting menu item missing\n";
            return 1;
        }
        autoroute_item->trigger();
        QApplication::processEvents();
        const bool menu_fired = tb && tb->autoroutingButton && tb->autoroutingButton->isChecked();
        const bool menu_thread = hdlg && hdlg->interactive_action_thread
            && (hdlg->is_board_read_only() || hdlg->interactive_action_thread->isAlive());
        if (!menu_fired && !menu_thread) {
            std::cerr << "gui-smoke: Autorouting menu did not fire on first trigger\n";
            return 1;
        }
        wait_action_thread_stop();
        if (tb && tb->autoroutingButton)
            tb->autoroutingButton->setChecked(false);
        if (!tb || !tb->autoroutingButton) {
            std::cerr << "gui-smoke: autorouting toolbar button missing\n";
            return 1;
        }
        QApplication::processEvents();
        tb->autoroutingButton->show();
        tb->show();
        QApplication::processEvents();
        if (tb->autoroutingButton->height() < 16 || tb->autoroutingButton->width() < 16) {
            std::cerr << "gui-smoke: autorouting button clipped ("
                      << tb->autoroutingButton->width() << "x"
                      << tb->autoroutingButton->height() << ")\n";
            return 1;
        }
        const QPoint btn_c(qMax(1, tb->autoroutingButton->width() / 2),
                           qMax(1, tb->autoroutingButton->height() / 2));
        const QPoint btn_in_tb = tb->autoroutingButton->mapTo(tb, btn_c);
        if (!tb->rect().contains(btn_in_tb)) {
            std::cerr << "gui-smoke: autorouting button outside toolbar "
                      << btn_in_tb.x() << "," << btn_in_tb.y()
                      << " tb " << tb->width() << "x" << tb->height() << "\n";
            return 1;
        }
        const QPoint in_frame = tb->autoroutingButton->mapTo(frame, btn_c);
        QWidget* hit = frame->childAt(in_frame);
        if (hit) {
            for (QWidget* w = hit; w && w != frame; w = w->parentWidget()) {
                if (auto* menu = qobject_cast<QMenu*>(w)) {
                    std::cerr << "gui-smoke: autorouting button covered by QMenu '"
                              << menu->title().toStdString() << "'\n";
                    return 1;
                }
            }
        }
        if (hit && hit != tb->autoroutingButton && !tb->autoroutingButton->isAncestorOf(hit)
            && dynamic_cast<gui::BoardPanel*>(hit)) {
            std::cerr << "gui-smoke: autorouting button covered by board panel\n";
            return 1;
        }
        send_mouse(tb->autoroutingButton, QEvent::MouseButtonPress, btn_c, Qt::LeftButton, Qt::LeftButton);
        send_mouse(tb->autoroutingButton, QEvent::MouseButtonRelease, btn_c, Qt::LeftButton, Qt::NoButton);
        QApplication::processEvents();
        const bool tb_fired = tb->autoroutingButton->isChecked();
        const bool tb_thread = hdlg && hdlg->interactive_action_thread
            && (hdlg->is_board_read_only() || hdlg->interactive_action_thread->isAlive());
        if (!tb_fired && !tb_thread) {
            std::cerr << "gui-smoke: autorouting toolbar click ignored\n";
            return 1;
        }
        wait_action_thread_stop();
        if (tb->autoroutingButton)
            tb->autoroutingButton->setChecked(false);
    }
    const QPoint local(180, 160);
    send_mouse(panel, QEvent::MouseMove, local, Qt::NoButton, Qt::NoButton);
    send_mouse(panel, QEvent::MouseButtonPress, local, Qt::LeftButton, Qt::LeftButton);
    send_mouse(panel, QEvent::MouseMove, local + QPoint(12, 8), Qt::NoButton, Qt::LeftButton);
    send_mouse(panel, QEvent::MouseButtonRelease, local + QPoint(12, 8), Qt::LeftButton, Qt::NoButton);
    send_mouse(panel, QEvent::MouseButtonPress, local, Qt::RightButton, Qt::RightButton);
    send_mouse(panel, QEvent::MouseButtonRelease, local, Qt::RightButton, Qt::NoButton);
    QApplication::processEvents();
    {
        java::awt::Point as_point(local.x(), local.y());
        java::awt::geom::Point2D* from_point = java::narrow<java::awt::geom::Point2D*>(as_point);
        if (!from_point) {
            std::cerr << "gui-smoke: Point→Point2D* narrow returned null\n";
            return 1;
        }
        if (!panel->right_button_click_location) {
            std::cerr << "gui-smoke: right-click location not stored\n";
            return 1;
        }
        panel->center_display(panel->right_button_click_location);
        QApplication::processEvents();
    }
    {
        const QPoint zoom_at(180, 160);
        send_mouse(panel, QEvent::MouseMove, zoom_at, Qt::NoButton, Qt::NoButton);
        auto* hdlg = panel->board_handling;
        auto* xform = (hdlg && hdlg->graphics_context) ? hdlg->graphics_context->coordinate_transform : nullptr;
        if (!xform) {
            std::cerr << "gui-smoke: missing coordinate transform for wheel zoom\n";
            return 1;
        }
        auto* screen0 = new java::awt::geom::Point2D(zoom_at.x(), zoom_at.y());
        auto* board_pt = xform->screen_to_board(screen0);
        const java::awt::Point vp0 = panel->get_viewport_position();
        const double view_x0 = zoom_at.x() - vp0.x;
        const double view_y0 = zoom_at.y() - vp0.y;
        send_wheel(panel, zoom_at, 120);
        xform = hdlg->graphics_context->coordinate_transform;
        auto* screen1 = xform->board_to_screen(board_pt);
        const java::awt::Point vp1 = panel->get_viewport_position();
        if (!screen1) {
            std::cerr << "gui-smoke: wheel zoom lost board point\n";
            return 1;
        }
        const double view_x1 = screen1->getX() - vp1.x;
        const double view_y1 = screen1->getY() - vp1.y;
        if (std::abs(view_x1 - view_x0) > 8.0 || std::abs(view_y1 - view_y0) > 8.0) {
            std::cerr << "gui-smoke: wheel zoom did not keep point under cursor"
                      << " view0=" << view_x0 << "," << view_y0
                      << " view1=" << view_x1 << "," << view_y1 << "\n";
            return 1;
        }
    }
    frame->zoom_all();
    QApplication::processEvents();
    frame->resize(frame->size() + QSize(90, 70));
    QApplication::processEvents();
    panel->repaint();
    QApplication::processEvents();
    {
        QWidget* vp = frame->scroll_pane ? frame->scroll_pane->viewport() : nullptr;
        QWidget* src = (vp && vp->width() >= 8 && vp->height() >= 8) ? static_cast<QWidget*>(vp) : panel;
        QSize sz = src->size().boundedTo(QSize(800, 600));
        if (sz.width() < 8 || sz.height() < 8) {
            std::cerr << "gui-smoke: board panel has no size\n";
            return 1;
        }
        QImage img(sz, QImage::Format_RGB32);
        img.fill(QColor(1, 2, 3));
        src->render(&img, QPoint(), QRegion(0, 0, sz.width(), sz.height()));
        QRgb seen[8];
        int nseen = 0;
        for (int y = 0; y < img.height() && nseen < 8; y += 2) {
            for (int x = 0; x < img.width() && nseen < 8; x += 2) {
                const QRgb px = img.pixel(x, y);
                bool found = false;
                for (int i = 0; i < nseen; ++i) {
                    if (seen[i] == px) {
                        found = true;
                        break;
                    }
                }
                if (!found)
                    seen[nseen++] = px;
            }
        }
        if (nseen < 2) {
            std::cerr << "gui-smoke: board panel appears empty (panel "
                      << panel->width() << "x" << panel->height() << ")\n";
            return 1;
        }
    }
    {
        gui::BoardToolbar* tb = frame->toolbar_panel;
        const int tb_h = tb ? tb->height() : 0;
        const int tb_w = tb ? tb->width() : 0;
        const bool btn_ok = tb && tb->autoroutingButton && tb->autoroutingButton->isVisible()
            && tb->autoroutingButton->width() > 0 && tb->autoroutingButton->height() > 0;
        const int btn_w = (tb && tb->autoroutingButton) ? tb->autoroutingButton->width() : 0;
        const int btn_h = (tb && tb->autoroutingButton) ? tb->autoroutingButton->height() : 0;
        if (!tb || !tb->isVisible() || tb_h < 24 || tb_w < 80 || tb_h > 90 || !btn_ok
            || btn_w > 36 || btn_h > 36) {
            std::cerr << "gui-smoke: toolbar not visible ( "
                      << tb_w << "x" << tb_h << " visible=" << (tb && tb->isVisible())
                      << " btn=" << btn_ok << " btn_sz=" << btn_w << "x" << btn_h << " )\n";
            return 1;
        }
        if (tb->unit_combo_box && tb->unit_combo_box->count() > 0) {
            const QString ut = tb->unit_combo_box->itemText(0);
            if (ut.contains(QLatin1String("Object@")) || ut.size() < 2) {
                std::cerr << "gui-smoke: unit combo shows " << ut.toStdString() << "\n";
                return 1;
            }
        }
        if (tb->autoroutingButton && tb->routingButton && tb->selectButton && tb->dragButton) {
            const int ax = tb->autoroutingButton->mapTo(tb, QPoint(0, 0)).x();
            const int rx = tb->routingButton->mapTo(tb, QPoint(0, 0)).x();
            const int sx = tb->selectButton->mapTo(tb, QPoint(0, 0)).x();
            const int dx = tb->dragButton->mapTo(tb, QPoint(0, 0)).x();
            if (!(ax < rx && rx < sx && sx < dx)) {
                std::cerr << "gui-smoke: toolbar order not autoroute, route, select, drag ("
                          << ax << "," << rx << "," << sx << "," << dx << ")\n";
                return 1;
            }
        }
        frame->highlight_selected_button();
        frame->set_select_toolbar();
        QApplication::processEvents();
        auto* st = frame->select_toolbar;
        if (!st || !st->isVisible() || st->height() < 24) {
            std::cerr << "gui-smoke: select toolbar not visible (h="
                      << (st ? st->height() : 0) << ")\n";
            return 1;
        }
        frame->set_menu_toolbar();
        QApplication::processEvents();
        if (!tb->isVisible() || tb->height() < 24) {
            std::cerr << "gui-smoke: menu toolbar missing after swap\n";
            return 1;
        }
    }
    QApplication::processEvents();
    bool oversized = false;
    auto show_hide = [&](QWidget* w) {
        if (!w)
            return;
        w->setVisible(true);
        QApplication::processEvents();
        if (w != frame && w->width() >= 1150 && w->height() >= 890)
            oversized = true;
        w->setVisible(false);
        QApplication::processEvents();
    };
    if (frame->permanent_subwindows.length > 0) {
        for (int32_t i = 0; i < frame->permanent_subwindows.length; ++i)
            show_hide(frame->permanent_subwindows[i]);
    } else {
        show_hide(frame->clearance_matrix_window);
        show_hide(frame->color_manager);
        show_hide(frame->via_window);
    }
    if (oversized) {
        std::cerr << "gui-smoke: a subwindow packed to 1150x900\n";
        return 1;
    }
    if (!frame->object_visibility_window || frame->object_visibility_window->message_arr.length < 1) {
        std::cerr << "gui-smoke: object visibility missing labels\n";
        return 1;
    }
    for (int32_t i = 0; i < frame->object_visibility_window->message_arr.length; ++i) {
        auto* lab = frame->object_visibility_window->message_arr[i];
        const QString t = lab ? lab->text() : QString();
        if (t.isEmpty() || t.contains(QLatin1String("Object@"))) {
            std::cerr << "gui-smoke: object visibility label " << i << " is "
                      << t.toStdString() << "\n";
            return 1;
        }
    }
    {
        const QString t0 = frame->object_visibility_window->message_arr[0]->text();
        if (!t0.contains(QLatin1String("trace"), Qt::CaseInsensitive)) {
            std::cerr << "gui-smoke: object visibility first label "
                      << t0.toStdString() << "\n";
            return 1;
        }
    }
    if (frame->clearance_matrix_window && frame->clearance_matrix_window->clearance_table) {
        auto* t = frame->clearance_matrix_window->clearance_table;
        if (t->rowCount() <= 0) {
            std::cerr << "gui-smoke: clearance table empty\n";
            return 1;
        }
        java::lang::Object* v00 = t->getValueAt(0, 0);
        if (!v00 || v00->toString().isEmpty()) {
            std::cerr << "gui-smoke: clearance getValueAt(0,0) empty\n";
            return 1;
        }
        if (auto* cb = frame->clearance_matrix_window->layer_combo_box) {
            if (cb->count() > 1) {
                cb->setSelectedIndex(0);
                java::lang::Object* o0 = cb->getSelectedItem();
                cb->setSelectedIndex(1);
                java::lang::Object* o1 = cb->getSelectedItem();
                if (o0 == o1) {
                    std::cerr << "gui-smoke: ComboBoxLayer index 1 same as 0\n";
                    return 1;
                }
                const QString t0 = cb->itemText(0);
                const QString t1 = cb->itemText(1);
                if (t0.contains(QLatin1String("Object@")) || t1.contains(QLatin1String("Object@"))
                    || t0 == t1 || t0.isEmpty()) {
                    std::cerr << "gui-smoke: ComboBoxLayer text " << t0.toStdString()
                              << " / " << t1.toStdString() << "\n";
                    return 1;
                }
            }
        }
        auto* model = frame->clearance_matrix_window->clearance_table_model;
        if (model && model->getRowCount() > 1 && model->getColumnCount() > 2
            && model->isCellEditable(1, 2)) {
            java::lang::Object* before = model->getValueAt(1, 2);
            model->setValueAt(java::lang::Float::valueOf(0.25f), 1, 2);
            java::lang::Object* after = model->getValueAt(1, 2);
            if (!after) {
                std::cerr << "gui-smoke: clearance setValueAt did not stick\n";
                return 1;
            }
            (void)before;
        }
    }
    if (frame->color_manager && frame->color_manager->item_color_table) {
        auto* ct = frame->color_manager->item_color_table;
        if (ct->rowCount() <= 0) {
            std::cerr << "gui-smoke: color table empty\n";
            return 1;
        }
        if (ct->model_) {
            const QString cn = ct->model_->getColumnName(1);
            if (cn.contains(QLatin1String("Object@"))) {
                std::cerr << "gui-smoke: color table column " << cn.toStdString() << "\n";
                return 1;
            }
        }
        if (ct->default_editor_) {
            java::lang::Object* cv = nullptr;
            for (int c = 0; c < ct->columnCount(); ++c) {
                QColor tmp;
                if (java::awt::color_from_object(ct->getValueAt(0, c), &tmp)) {
                    cv = ct->getValueAt(0, c);
                    break;
                }
            }
            if (cv) {
                ct->default_editor_->prepareForEdit(cv, 0, 1);
                java::lang::Object* ev = ct->default_editor_->getCellEditorValue();
                QColor got;
                if (!java::awt::color_from_object(ev, &got)) {
                    std::cerr << "gui-smoke: ColorEditor getCellEditorValue not a color\n";
                    return 1;
                }
            }
        }
    }
    if (frame->edit_net_rules_window && frame->edit_net_rules_window->table) {
        if (frame->edit_net_rules_window->table->rowCount() <= 0) {
            std::cerr << "gui-smoke: net class table empty\n";
            return 1;
        }
    }
    {
        QMenuBar* mb = frame->menuBar();
        if (!mb || mb->actions().size() < 5) {
            std::cerr << "gui-smoke: menubar top-level count "
                      << (mb ? mb->actions().size() : 0) << "\n";
            return 1;
        }
        bool has_sub = false;
        QMenu* utilities = nullptr;
        for (auto* a : mb->actions()) {
            if (!a || !a->menu())
                continue;
            if (a->menu()->actions().size() >= 2)
                has_sub = true;
            const QString t = a->text().isEmpty() ? a->menu()->title() : a->text();
            if (t.contains(QLatin1String("Utilities"), Qt::CaseInsensitive)
                || t.contains(QString::fromUtf8("Dienst")))
                utilities = a->menu();
        }
        if (!has_sub) {
            std::cerr << "gui-smoke: menubar has no submenu\n";
            return 1;
        }
        int nested = 0;
        QAction* first_nested = nullptr;
        if (utilities) {
            for (auto* it : utilities->actions()) {
                if (it && it->menu() && it->menu()->actions().size() >= 1) {
                    if (it->text().trimmed().isEmpty() && it->menu()->title().trimmed().isEmpty()) {
                        std::cerr << "gui-smoke: Utilities nested menu has empty title\n";
                        return 1;
                    }
                    ++nested;
                    if (!first_nested)
                        first_nested = it;
                }
            }
        }
        if (!utilities || nested < 4) {
            std::cerr << "gui-smoke: Utilities nested menus "
                      << nested << " (need Display/Parameter/Rules/Info)\n";
            if (utilities) {
                for (auto* it : utilities->actions()) {
                    const QString t = it ? it->text() : QString();
                    std::cerr << "  item '" << t.toStdString() << "' menu="
                              << (it && it->menu() ? 1 : 0)
                              << " n=" << (it && it->menu() ? it->menu()->actions().size() : 0)
                              << "\n";
                }
            }
            return 1;
        }
        utilities->popup(QPoint(80, 80));
        QApplication::processEvents();
        if (first_nested) {
            const QRect nr = utilities->actionGeometry(first_nested);
            send_mouse(utilities, QEvent::MouseMove, nr.center(), Qt::NoButton, Qt::NoButton);
            utilities->setActiveAction(first_nested);
            QApplication::processEvents();
            if (!first_nested->menu() || !first_nested->menu()->isVisible()) {
                std::cerr << "gui-smoke: Utilities nested menu not visible on hover\n";
                return 1;
            }
        }
        utilities->hide();
        QApplication::processEvents();
        if (panel->popup_menu_main) {
            bool zoom_sub = false;
            for (auto* a : panel->popup_menu_main->actions()) {
                if (a && a->menu() && a->menu()->actions().size() >= 2)
                    zoom_sub = true;
            }
            if (!zoom_sub) {
                std::cerr << "gui-smoke: popup Zoom is not a submenu\n";
                return 1;
            }
        }
        if (panel->popup_menu_dynamic_route) {
            int route_subs = 0;
            for (auto* a : panel->popup_menu_dynamic_route->actions()) {
                if (a && a->menu() && a->menu()->actions().size() >= 1)
                    ++route_subs;
            }
            if (route_subs < 2) {
                std::cerr << "gui-smoke: route popup missing Change Layer submenu ("
                          << route_subs << ")\n";
                return 1;
            }
        }
    }
    {
        auto* hdlg = panel->board_handling;
        hdlg->key_typed_action('c');
        QApplication::processEvents();
        hdlg->key_typed_action('a');
        QApplication::processEvents();
        QKeyEvent ke(QEvent::KeyPress, Qt::Key_C, Qt::NoModifier, QStringLiteral("c"));
        QApplication::sendEvent(panel, &ke);
        QApplication::processEvents();
        hdlg->set_select_menu_state();
        QApplication::processEvents();
        if (!dynamic_cast<interactive::SelectMenuState*>(hdlg->get_interactive_state())) {
            std::cerr << "gui-smoke: set_select_menu_state did not enter SelectMenuState\n";
            return 1;
        }
        board::Pin* pin = nullptr;
        if (auto* items = hdlg->get_routing_board()->get_items()) {
            auto* it = items->iterator();
            while (it && it->hasNext()) {
                board::Item* item = it->next();
                if (auto* p = dynamic_cast<board::Pin*>(item)) {
                    pin = p;
                    break;
                }
            }
            delete it;
        }
        if (pin && hdlg->graphics_context && hdlg->graphics_context->coordinate_transform) {
            auto* fp = pin->get_center() ? pin->get_center()->to_float() : nullptr;
            java::awt::geom::Point2D* scr =
                hdlg->graphics_context->coordinate_transform->board_to_screen(fp);
            if (scr)
                hdlg->left_button_clicked(scr);
            QApplication::processEvents();
        }
        hdlg->set_route_menu_state();
        QApplication::processEvents();
        if (!dynamic_cast<interactive::RouteMenuState*>(hdlg->get_interactive_state())) {
            std::cerr << "gui-smoke: set_route_menu_state did not enter RouteMenuState\n";
            return 1;
        }
        if (pin && hdlg->graphics_context && hdlg->graphics_context->coordinate_transform) {
            auto* fp = pin->get_center() ? pin->get_center()->to_float() : nullptr;
            java::awt::geom::Point2D* scr =
                hdlg->graphics_context->coordinate_transform->board_to_screen(fp);
            if (scr) {
                const QPoint pt(qRound(scr->x()), qRound(scr->y()));
#if QT_VERSION >= QT_VERSION_CHECK(6, 0, 0)
                QMouseEvent press(QEvent::MouseButtonPress, QPointF(pt),
                                   Qt::LeftButton, Qt::LeftButton, Qt::NoModifier);
                QMouseEvent release(QEvent::MouseButtonRelease, QPointF(pt),
                                     Qt::LeftButton, Qt::NoButton, Qt::NoModifier);
                QMouseEvent dbl(QEvent::MouseButtonDblClick, QPointF(pt),
                                 Qt::LeftButton, Qt::LeftButton, Qt::NoModifier);
                QMouseEvent rel2(QEvent::MouseButtonRelease, QPointF(pt),
                                  Qt::LeftButton, Qt::NoButton, Qt::NoModifier);
                QMouseEvent move(QEvent::MouseMove, QPointF(pt + QPoint(8, 8)),
                                 Qt::NoButton, Qt::NoButton, Qt::NoModifier);
#else
                QMouseEvent press(QEvent::MouseButtonPress, pt, Qt::LeftButton,
                                   Qt::LeftButton, Qt::NoModifier);
                QMouseEvent release(QEvent::MouseButtonRelease, pt, Qt::LeftButton,
                                     Qt::NoButton, Qt::NoModifier);
                QMouseEvent dbl(QEvent::MouseButtonDblClick, pt, Qt::LeftButton,
                                 Qt::LeftButton, Qt::NoModifier);
                QMouseEvent rel2(QEvent::MouseButtonRelease, pt, Qt::LeftButton,
                                  Qt::NoButton, Qt::NoModifier);
                QMouseEvent move(QEvent::MouseMove, pt + QPoint(8, 8), Qt::NoButton,
                                 Qt::NoButton, Qt::NoModifier);
#endif
                QApplication::sendEvent(panel, &press);
                QApplication::sendEvent(panel, &release);
                QApplication::processEvents();
                auto* after = hdlg->get_interactive_state();
                if (!dynamic_cast<interactive::RouteState*>(after)
                    || dynamic_cast<interactive::RouteMenuState*>(after)) {
                    std::cerr << "gui-smoke: pin click did not start routing\n";
                    return 1;
                }
                if (panel->popup_menu_dynamic_route) {
                    send_mouse(panel, QEvent::MouseButtonPress, pt, Qt::RightButton, Qt::RightButton);
                    send_mouse(panel, QEvent::MouseButtonRelease, pt, Qt::RightButton, Qt::NoButton);
                    java::swing::JPopupMenu* popup = hdlg->get_current_popup_menu();
                    if (!popup || !popup->isVisible()) {
                        std::cerr << "gui-smoke: route popup not visible after right-click\n";
                        return 1;
                    }
                    QAction* layer_act = nullptr;
                    QMenu* layer_menu = nullptr;
                    QAction* change_layer_act = nullptr;
                    for (QAction* a : popup->actions()) {
                        QMenu* sub = a ? a->menu() : nullptr;
                        if (!sub)
                            continue;
                        const QString t = sub->title().isEmpty() ? a->text() : sub->title();
                        if (!t.contains(QLatin1String("layer"), Qt::CaseInsensitive)
                            && !t.contains(QString::fromUtf8("Lage")))
                            continue;
                        change_layer_act = a;
                        layer_menu = sub;
                        for (QAction* la : sub->actions()) {
                            if (la && la->isEnabled()) {
                                layer_act = la;
                                break;
                            }
                        }
                        break;
                    }
                    if (!layer_act || !layer_menu || !change_layer_act) {
                        std::cerr << "gui-smoke: change-layer menu item missing\n";
                        return 1;
                    }
                    const QRect sub_r = popup->actionGeometry(change_layer_act);
                    send_mouse(popup, QEvent::MouseMove, sub_r.center(), Qt::NoButton, Qt::NoButton);
                    popup->setActiveAction(change_layer_act);
                    QApplication::processEvents();
                    if (!layer_menu->isVisible()) {
                        std::cerr << "gui-smoke: change-layer submenu not visible\n";
                        return 1;
                    }
                    const QRect layer_r = layer_menu->actionGeometry(layer_act);
                    click_widget(layer_menu, layer_r.center(), Qt::LeftButton);
                    QApplication::processEvents();
                }
                QApplication::sendEvent(panel, &dbl);
                QApplication::sendEvent(panel, &rel2);
                QApplication::processEvents();
                after = hdlg->get_interactive_state();
                if (dynamic_cast<interactive::RouteMenuState*>(after)) {
                    std::cerr << "gui-smoke: route aborted on extra mouse release\n";
                    return 1;
                }
                QApplication::sendEvent(panel, &move);
                QApplication::processEvents();
                after = hdlg->get_interactive_state();
                if (dynamic_cast<interactive::RouteMenuState*>(after)) {
                    std::cerr << "gui-smoke: route aborted after mouse move\n";
                    return 1;
                }
                hdlg->cancel_state();
                QApplication::processEvents();
                hdlg->set_route_menu_state();
                QApplication::processEvents();
                auto* pin_fp = pin->get_center()->to_float();
                auto* parent = hdlg->get_interactive_state();
                auto* rs = interactive::RouteState::get_instance(
                    pin_fp, parent, hdlg, hdlg->logfile);
                if (!rs || !rs->route) {
                    std::cerr << "gui-smoke: via-engine RouteState::get_instance failed\n";
                    return 1;
                }
                hdlg->set_interactive_state(rs);
                QApplication::processEvents();
                board::RoutingBoard* rb = hdlg->get_routing_board();
                std::vector<geometry::planar::IntBox*> pin_boxes;
                if (auto* items = rb->get_items()) {
                    auto* it = items->iterator();
                    while (it && it->hasNext()) {
                        board::Item* item = it->next();
                        if (auto* p = dynamic_cast<board::Pin*>(item)) {
                            if (auto* bb = p->bounding_box())
                                pin_boxes.push_back(bb);
                        }
                    }
                    delete it;
                }
                const double via_clear = 600.0;
                auto blocked = [&](double x, double y) {
                    for (auto* bb : pin_boxes) {
                        if (!bb || !bb->ll || !bb->ur)
                            continue;
                        if (x >= bb->ll->x - via_clear && x <= bb->ur->x + via_clear
                            && y >= bb->ll->y - via_clear && y <= bb->ur->y + via_clear)
                            return true;
                    }
                    return false;
                };
                auto* box = rb->get_bounding_box();
                const double via_margin = 1000.0;
                auto inside = [&](double x, double y) {
                    if (!box || !box->ll || !box->ur)
                        return false;
                    return x >= box->ll->x + via_margin && x <= box->ur->x - via_margin
                        && y >= box->ll->y + via_margin && y <= box->ur->y - via_margin;
                };
                auto last_fp = [&]() -> geometry::planar::FloatPoint* {
                    auto* last = rs->route ? rs->route->get_last_corner() : nullptr;
                    return (last && last->to_float()) ? last->to_float() : nullptr;
                };
                // 90° routing only advances one axis per add_corner. Walk
                // Manhattan to the board centre so the via is not left on the
                // pin pad or against the outline.
                double cx = pin_fp->x + 2000.0;
                double cy = pin_fp->y;
                if (box && box->ll && box->ur) {
                    cx = 0.5 * (box->ll->x + box->ur->x);
                    cy = 0.5 * (box->ll->y + box->ur->y);
                }
                rs->add_corner(new geometry::planar::FloatPoint(cx, pin_fp->y));
                QApplication::processEvents();
                rs->add_corner(new geometry::planar::FloatPoint(cx, cy));
                QApplication::processEvents();
                auto* lf = last_fp();
                if (!lf || std::hypot(lf->x - pin_fp->x, lf->y - pin_fp->y) < 400.0
                    || !inside(lf->x, lf->y) || blocked(lf->x, lf->y)) {
                    std::vector<std::pair<double, double>> candidates;
                    if (box && box->ll && box->ur) {
                        const double x0 = box->ll->x, y0 = box->ll->y;
                        const double w = box->ur->x - box->ll->x;
                        const double h = box->ur->y - box->ll->y;
                        for (int ix = 2; ix <= 4; ++ix) {
                            for (int iy = 2; iy <= 4; ++iy)
                                candidates.emplace_back(x0 + ix * w / 6.0, y0 + iy * h / 6.0);
                        }
                    }
                    lf = last_fp();
                    for (auto& c : candidates) {
                        if (!inside(c.first, c.second) || blocked(c.first, c.second))
                            continue;
                        rs->add_corner(new geometry::planar::FloatPoint(c.first, pin_fp->y));
                        QApplication::processEvents();
                        rs->add_corner(new geometry::planar::FloatPoint(c.first, c.second));
                        QApplication::processEvents();
                        lf = last_fp();
                        if (lf && std::hypot(lf->x - pin_fp->x, lf->y - pin_fp->y) > 400.0
                            && inside(lf->x, lf->y) && !blocked(lf->x, lf->y))
                            break;
                    }
                }
                lf = last_fp();
                if (!lf || std::hypot(lf->x - pin_fp->x, lf->y - pin_fp->y) < 400.0
                    || !inside(lf->x, lf->y) || blocked(lf->x, lf->y)) {
                    std::cerr << "gui-smoke: add_corner did not leave pin"
                              << " last=" << (lf ? lf->x : 0) << "," << (lf ? lf->y : 0)
                              << " pin=" << pin_fp->x << "," << pin_fp->y << "\n";
                    return 1;
                }
                auto count_vias = [&]() {
                    int n = 0;
                    if (auto* items = rb->get_items()) {
                        auto* it = items->iterator();
                        while (it && it->hasNext()) {
                            board::Item* item = it->next();
                            if (dynamic_cast<board::Via*>(item))
                                ++n;
                        }
                        delete it;
                    }
                    return n;
                };
                int dest = -1;
                auto* ls = rb->layer_structure;
                const int cur = hdlg->settings->get_layer();
                for (int i = 0; i < ls->arr.length; ++i) {
                    if (i != cur && ls->arr[i] && ls->arr[i]->is_signal) {
                        dest = i;
                        break;
                    }
                }
                if (dest >= 0) {
                    const int vias0 = count_vias();
                    rs->route->via_snap_to_smd_center = false;
                    const bool ok = rs->change_layer_action(dest);
                    const int vias1 = count_vias();
                    auto* last = rs->route ? rs->route->get_last_corner() : nullptr;
                    auto* lf = (last && last->to_float()) ? last->to_float() : nullptr;
                    if (vias1 <= vias0) {
                        std::cerr << "gui-smoke: via not inserted at free location"
                                  << " last=" << (lf ? lf->x : 0) << "," << (lf ? lf->y : 0)
                                  << " pin=" << pin_fp->x << "," << pin_fp->y
                                  << " ok=" << (ok ? 1 : 0)
                                  << " dest=" << dest
                                  << " fail_layer=" << rb->get_shove_failing_layer();
                        if (auto* obs = rb->get_shove_failing_obstacle()) {
                            std::cerr << " obs=";
                            if (dynamic_cast<board::Pin*>(obs))
                                std::cerr << "Pin";
                            else if (dynamic_cast<board::PolylineTrace*>(obs))
                                std::cerr << "Trace";
                            else if (dynamic_cast<board::Via*>(obs))
                                std::cerr << "Via";
                            else if (dynamic_cast<board::BoardOutline*>(obs))
                                std::cerr << "Outline";
                            else
                                std::cerr << typeid(*obs).name();
                        }
                        std::cerr << "\n";
                        return 1;
                    }
                }
                hdlg->cancel_state();
                QApplication::processEvents();
            }
        }
        hdlg->set_drag_menu_state();
        QApplication::processEvents();
        hdlg->set_select_menu_state();
        if (pin && hdlg->graphics_context && hdlg->graphics_context->coordinate_transform) {
            auto* fp = pin->get_center() ? pin->get_center()->to_float() : nullptr;
            java::awt::geom::Point2D* scr =
                hdlg->graphics_context->coordinate_transform->board_to_screen(fp);
            if (scr)
                hdlg->left_button_clicked(scr);
            QApplication::processEvents();
        }
        {
            QTemporaryDir tmp;
            const QString logp = tmp.filePath(QStringLiteral("smoke.log"));
            {
                QFile f(logp);
                if (f.open(QIODevice::WriteOnly))
                    f.write("set_layer\n0\n");
            }
            auto* in = new java::io::FileInputStream(logp);
            hdlg->read_logfile(in);
            for (int i = 0; i < 50; ++i) {
                QApplication::processEvents();
                if (!hdlg->interactive_action_thread
                    || !hdlg->interactive_action_thread->isAlive())
                    break;
                QThread::msleep(10);
            }
            if (hdlg->interactive_action_thread
                && !hdlg->interactive_action_thread->isAlive())
                hdlg->interactive_action_thread->join();
            QApplication::processEvents();
        }
        {
            java::awt::Cursor* cross =
                java::awt::Cursor::getPredefinedCursor(java::awt::Cursor::CROSSHAIR_CURSOR);
            java::awt::Cursor* arrow =
                java::awt::Cursor::getPredefinedCursor(java::awt::Cursor::DEFAULT_CURSOR);
            if (!cross || cross == arrow) {
                std::cerr << "gui-smoke: getPredefinedCursor ignores type\n";
                return 1;
            }
            java::awt::Graphics2D g2;
            QImage img(8, 8, QImage::Format_ARGB32);
            QPainter qp(&img);
            g2.p = &qp;
            g2.setStroke(java::awt::BasicStroke(3.f, java::awt::BasicStroke::CAP_ROUND,
                                               java::awt::BasicStroke::JOIN_ROUND));
            if (g2.cap_style != Qt::RoundCap || g2.stroke < 2.f) {
                std::cerr << "gui-smoke: setStroke did not keep cap/width\n";
                return 1;
            }
            g2.setComposite(java::awt::AlphaComposite::getInstance(
                java::awt::AlphaComposite::DST_OVER, 0.4f));
            if (qp.compositionMode() != QPainter::CompositionMode_DestinationOver) {
                std::cerr << "gui-smoke: DST_OVER not applied\n";
                return 1;
            }
        }
        {
            QTemporaryDir tmp;
            const QString work = tmp.path();
            const QString dsn_copy = QDir(work).filePath(QStringLiteral("smoke.dsn"));
            QFile::copy(dsn, dsn_copy);
            java::io::ByteArrayOutputStream defaults_out;
            if (!gui::GUIDefaultsFile::write(frame, hdlg, &defaults_out)
                || defaults_out.buf.isEmpty()) {
                std::cerr << "gui-smoke: GUIDefaults write empty\n";
                return 1;
            }
            java::io::ByteArrayInputStream defaults_in(defaults_out.buf);
            if (!gui::GUIDefaultsFile::read(frame, hdlg, &defaults_in)) {
                std::cerr << "gui-smoke: GUIDefaults read failed\n";
                return 1;
            }
            gui::DesignFile* df_ses = gui::DesignFile::get_instance(dsn_copy);
            gui::BoardFrame* ses_frame = gui::MainApplication::createBoardFrame(
                df_ses, true, false, java::util::Locale::ENGLISH, false);
            if (!ses_frame) {
                std::cerr << "gui-smoke: -s frame failed\n";
                return 1;
            }
            ses_frame->show();
            QApplication::processEvents();
            ses_frame->close();
            QApplication::processEvents();
            const QString sesp = QDir(work).filePath(QStringLiteral("smoke.ses"));
            if (!QFileInfo::exists(sesp)) {
                std::cerr << "gui-smoke: -s did not write SES on close\n";
                return 1;
            }
            const QString binp = QDir(work).filePath(QStringLiteral("smoke.bin"));
            frame->design_file = gui::DesignFile::get_instance(dsn_copy);
            if (!frame->save() || !QFileInfo::exists(binp)) {
                std::cerr << "gui-smoke: File save .bin missing\n";
                return 1;
            }
            gui::DesignFile* df_bin = gui::DesignFile::get_instance(binp);
            gui::BoardFrame* bin_frame = gui::MainApplication::createBoardFrame(
                df_bin, false, false, java::util::Locale::ENGLISH, false);
            if (!bin_frame || !bin_frame->board_panel
                || !bin_frame->board_panel->board_handling
                || !bin_frame->board_panel->board_handling->get_routing_board()) {
                std::cerr << "gui-smoke: .bin reload failed\n";
                return 1;
            }
            java::io::ByteArrayOutputStream ses_buf;
            if (!hdlg->export_specctra_session_file(QStringLiteral("smoke.dsn"), &ses_buf)
                || ses_buf.buf.isEmpty()) {
                std::cerr << "gui-smoke: SES export via File API failed\n";
                return 1;
            }
            java::io::ByteArrayInputStream ses_in(ses_buf.buf);
            java::io::ByteArrayOutputStream eagle_out;
            if (!hdlg->export_eagle_session_file(&ses_in, &eagle_out)) {
                std::cerr << "gui-smoke: eagle export failed\n";
                return 1;
            }
            if (frame->toolbar_panel && frame->toolbar_panel->autoroutingButton) {
                hdlg->start_batch_autorouter();
                QApplication::processEvents();
                if (hdlg->interactive_action_thread) {
                    hdlg->interactive_action_thread->request_stop();
                    for (int i = 0; i < 40; ++i) {
                        QApplication::processEvents();
                        if (!hdlg->interactive_action_thread->isAlive())
                            break;
                        QThread::msleep(20);
                    }
                }
            }
        }
    }
    QString in = gui::input_text_dialog(frame, QStringLiteral("smoke"));
    if (in.isEmpty()) {
        std::cerr << "gui-smoke: showInputDialog returned null\n";
        return 1;
    }
    std::cout << "gui-smoke ok\n";
    return 0;
}
#endif

int main(int argc, char** argv)
{
    QStringList args;
    for (int i = 1; i < argc; ++i)
        args << QString::fromLocal8Bit(argv[i]);

    bool self = args.contains(QStringLiteral("--selftest"));
    bool help = args.contains(QStringLiteral("-h")) || args.contains(QStringLiteral("--help"));
    if (help && !self)
    {
        print_help();
        return 0;
    }
    if (self)
        return selftest();

    if (args.contains(QStringLiteral("--dump")) || args.contains(QStringLiteral("--ses"))
        || args.contains(QStringLiteral("--autoroute")) || args.contains(QStringLiteral("--manual-test")))
        return run_headless(args);

    // Helper inside layout.app: native menu bar would bind to LayoutEditor and
    // leave FreeRouting's QMenuBar empty/hidden. Must be set before QApplication.
    QCoreApplication::setAttribute(Qt::AA_DontUseNativeMenuBar);
    install_message_handler();
    QApplication app(argc, argv);
    app.setApplicationName(QStringLiteral("FreeRouting"));
    app.setApplicationVersion(QString::fromLatin1(VERSION));
    register_fr_qt_types();
    // Smoke/repro checks compare English labels; only an explicit -l changes them.
    const bool gui_test = args.contains(QStringLiteral("--gui-smoke")) || args.contains(QStringLiteral("--repro-change-layer"));
    const QString language = gui_test && !args.contains(QStringLiteral("-l"))
        ? QStringLiteral("en") : gui::translation_language(args);
    gui::install_translators(language);
    java::util::Locale::setDefault(java::util::Locale(language));

#ifdef FR_HAS_GUI_MAIN
    if (args.contains(QStringLiteral("--repro-change-layer"))) {
        QString dsn;
        const int sm = args.indexOf(QStringLiteral("--repro-change-layer"));
        if (sm >= 0 && sm + 1 < args.size() && !args[sm + 1].startsWith(QLatin1Char('-')))
            dsn = args[sm + 1];
        else {
            const int de = args.indexOf(QStringLiteral("-de"));
            if (de >= 0 && de + 1 < args.size())
                dsn = args[de + 1];
        }
        return run_repro_change_layer(dsn);
    }
    if (args.contains(QStringLiteral("--gui-smoke"))) {
        QString dsn;
        const int sm = args.indexOf(QStringLiteral("--gui-smoke"));
        if (sm >= 0 && sm + 1 < args.size() && !args[sm + 1].startsWith(QLatin1Char('-')))
            dsn = args[sm + 1];
        else {
            const int de = args.indexOf(QStringLiteral("-de"));
            if (de >= 0 && de + 1 < args.size())
                dsn = args[de + 1];
        }
        return run_gui_smoke(dsn);
    }
#endif

    java::Array<QString> jargs(args.size());
    for (int i = 0; i < args.size(); ++i)
        jargs[i] = args[i];

#ifdef FR_HAS_GUI_MAIN
    gui::MainApplication::main(jargs);
    return app.exec();
#else
    if (args.contains(QStringLiteral("-de")) && args.size() >= 2)
        std::cout << "loading_design "
                  << args.value(args.indexOf(QStringLiteral("-de")) + 1).toStdString() << "\n";
    std::cerr << "FreeRouting Qt: GUI not linked in this build, use --selftest / --dump / -h\n";
    return 1;
#endif
}
