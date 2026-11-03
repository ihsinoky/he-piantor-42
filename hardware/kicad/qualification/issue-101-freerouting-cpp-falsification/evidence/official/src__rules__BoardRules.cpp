#include "rules/BoardRules.h"
#include "rules/fr_package.h"
#include "geometry/planar/ConvexShape.h"
#include "board/AngleRestriction.h"
#include "board/Layer.h"
#include "board/LayerStructure.h"
#include "board/Item.h"
#include "library/Padstack.h"
#include "geometry/planar/ConvexShape.h"
#include "board/Item.h"
#include "board/Pin.h"
#include "board/BasicBoard.h"

namespace rules {
BoardRules::BoardRules(board::LayerStructure* p_layer_structure, rules::ClearanceMatrix* p_clearance_matrix) {
    this->ignore_conduction = true;
    this->via_infos = new rules::ViaInfos();
    this->via_rules = new java::util::Vector<rules::ViaRule*>();
    this->net_classes = new rules::NetClasses();
    this->slow_autoroute_algorithm = false;
    (java::fr_assign(this->layer_structure, p_layer_structure));
    (java::fr_assign(this->clearance_matrix, p_clearance_matrix));
    (java::fr_assign(this->nets, new rules::Nets()));
    (java::fr_assign(this->trace_angle_restriction, board::AngleRestriction::FORTYFIVE_DEGREE));
    (java::fr_assign(this->min_trace_half_width, 100000));
    (java::fr_assign(this->max_trace_half_width, 100));
}

BoardRules::BoardRules() {
    this->ignore_conduction = true;
    this->via_infos = new rules::ViaInfos();
    this->via_rules = new java::util::Vector<rules::ViaRule*>();
    this->net_classes = new rules::NetClasses();
    this->slow_autoroute_algorithm = false;
}

int32_t BoardRules::get_trace_half_width(int32_t p_net_no, int32_t p_layer) {
    rules::Net* curr_net = java::narrow<rules::Net*>(nets->get(p_net_no));
    return java::fr_num(curr_net->get_class()->get_trace_half_width(java::fr_num(p_layer)));
}

bool BoardRules::trace_widths_are_layer_dependent(int32_t p_net_no) {
    int32_t compare_width = java::fr_num(this->get_trace_half_width(java::fr_num(p_net_no), java::fr_num(0)));
    for (int32_t i = 1; (java::fr_cmp(i, this->layer_structure->arr.length) < 0); ++i) {
        if ((!java::fr_eq(this->get_trace_half_width(java::fr_num(p_net_no), java::fr_num(i)), compare_width))) {
            return java::fr_num(true);
        }
    }
    return java::fr_num(false);
}

int32_t BoardRules::get_min_trace_half_width() {
    return java::fr_num(this->min_trace_half_width);
}

int32_t BoardRules::get_max_trace_half_width() {
    return java::fr_num(this->max_trace_half_width);
}

void BoardRules::set_default_trace_half_width(int32_t p_layer, int32_t p_value) {
    this->get_default_net_class()->set_trace_half_width(java::fr_num(p_layer), java::fr_num(p_value));
    (java::fr_assign(this->min_trace_half_width, java::lang::Math::min(this->min_trace_half_width, p_value)));
    (java::fr_assign(this->max_trace_half_width, java::lang::Math::max(this->max_trace_half_width, p_value)));
}

int32_t BoardRules::get_default_trace_half_width(int32_t p_layer) {
    return java::fr_num(this->get_default_net_class()->get_trace_half_width(java::fr_num(p_layer)));
}

void BoardRules::set_default_trace_half_widths(int32_t p_value) {
    if ((java::fr_cmp(p_value, 0) <= 0)) {
        java::lang::System::out.println(QString::fromUtf8("\x42\x6f\x61\x72\x64\x52\x75\x6c\x65\x73\x2e\x73\x65\x74\x5f\x74\x72\x61\x63\x65\x5f\x68\x61\x6c\x66\x5f\x77\x69\x64\x74\x68\x73\x3a\x20\x70\x5f\x76\x61\x6c\x75\x65\x20\x6f\x75\x74\x20\x6f\x66\x20\x72\x61\x6e\x67\x65", 54));
        return;
    }
    this->get_default_net_class()->set_trace_half_width(java::fr_num(p_value));
    (java::fr_assign(this->min_trace_half_width, java::lang::Math::min(this->min_trace_half_width, p_value)));
    (java::fr_assign(this->max_trace_half_width, java::lang::Math::max(this->max_trace_half_width, p_value)));
}

rules::NetClass* BoardRules::get_default_net_class() {
    if ((java::fr_cmp(this->net_classes->count(), 0) <= 0)) {
        this->create_default_net_class();
    }
    return java::narrow<rules::NetClass*>(this->net_classes->get(0));
}

int32_t BoardRules::default_clearance_class() {
    return java::fr_num(1);
}

int32_t BoardRules::clearance_class_none() {
    return java::fr_num(0);
}

rules::NetClass* BoardRules::get_new_net_class(java::util::Locale p_locale) {
    rules::NetClass* result = java::narrow<rules::NetClass*>(this->net_classes->append(this->layer_structure, this->clearance_matrix, p_locale));
    result->set_trace_clearance_class(java::fr_num(this->get_default_net_class()->get_trace_clearance_class()));
    result->set_via_rule(java::narrow<rules::ViaRule*>(this->get_default_via_rule()));
    result->set_trace_half_width(java::fr_num(this->get_default_net_class()->get_trace_half_width(java::fr_num(0))));
    return java::narrow<rules::NetClass*>(result);
}

rules::NetClass* BoardRules::get_new_net_class(QString p_name) {
    rules::NetClass* result = java::narrow<rules::NetClass*>(this->net_classes->append(p_name, this->layer_structure, this->clearance_matrix));
    result->set_trace_clearance_class(java::fr_num(this->get_default_net_class()->get_trace_clearance_class()));
    result->set_via_rule(java::narrow<rules::ViaRule*>(this->get_default_via_rule()));
    result->set_trace_half_width(java::fr_num(this->get_default_net_class()->get_trace_half_width(java::fr_num(0))));
    return java::narrow<rules::NetClass*>(result);
}

void BoardRules::create_default_via_rule(rules::NetClass* p_net_class, QString p_name) {
    if (java::fr_eq(this->via_infos->count(), 0)) {
        return;
    }
    rules::ViaRule* default_rule = java::narrow<rules::ViaRule*>(new rules::ViaRule(p_name));
    int32_t default_via_cl_class = java::fr_num(p_net_class->default_item_clearance_classes->get(java::narrow<rules::DefaultItemClearanceClasses_ItemClass*>(rules::DefaultItemClearanceClasses_ItemClass::VIA)));
    for (int32_t i = 0; (java::fr_cmp(i, this->via_infos->count()) < 0); ++i) {
        rules::ViaInfo* curr_via_info = java::narrow<rules::ViaInfo*>(this->via_infos->get(i));
        if (java::fr_eq(curr_via_info->get_clearance_class(), default_via_cl_class)) {
            library::Padstack* curr_padstack = java::narrow<library::Padstack*>(curr_via_info->get_padstack());
            int32_t curr_from_layer = java::fr_num(curr_padstack->from_layer());
            int32_t curr_to_layer = java::fr_num(curr_padstack->to_layer());
            rules::ViaInfo* existing_via = java::narrow<rules::ViaInfo*>(default_rule->get_layer_range(java::fr_num(curr_from_layer), java::fr_num(curr_to_layer)));
            if ((!java::fr_eq(existing_via, nullptr))) {
                geometry::planar::ConvexShape* new_shape = java::narrow<geometry::planar::ConvexShape*>(curr_padstack->get_shape(java::fr_num(curr_from_layer)));
                geometry::planar::ConvexShape* existing_shape = java::narrow<geometry::planar::ConvexShape*>(existing_via->get_padstack()->get_shape(java::fr_num(curr_from_layer)));
                if ((java::fr_cmp(new_shape->max_width(), existing_shape->max_width()) < 0)) {
                    default_rule->remove_via(java::narrow<rules::ViaInfo*>(existing_via));
                    default_rule->append_via(java::narrow<rules::ViaInfo*>(curr_via_info));
                }
            } else {
                default_rule->append_via(java::narrow<rules::ViaInfo*>(curr_via_info));
            }
        }
    }
    this->via_rules->add(default_rule);
    p_net_class->set_via_rule(java::narrow<rules::ViaRule*>(default_rule));
}

void BoardRules::create_default_net_class() {
    rules::NetClass* default_net_class = java::narrow<rules::NetClass*>(this->net_classes->append(QString::fromUtf8("\x64\x65\x66\x61\x75\x6c\x74", 7), this->layer_structure, this->clearance_matrix));
    int32_t default_trace_half_width = java::fr_num(1500);
    default_net_class->set_trace_half_width(java::fr_num(default_trace_half_width));
    default_net_class->set_trace_clearance_class(java::fr_num(1));
}

rules::NetClass* BoardRules::append_net_class(java::util::Locale p_locale) {
    rules::NetClass* new_class = java::narrow<rules::NetClass*>(this->net_classes->append(this->layer_structure, this->clearance_matrix, p_locale));
    rules::NetClass* default_class = java::narrow<rules::NetClass*>(this->net_classes->get(0));
    new_class->set_via_rule(java::narrow<rules::ViaRule*>(default_class->get_via_rule()));
    new_class->set_trace_half_width(java::fr_num(default_class->get_trace_half_width(java::fr_num(0))));
    new_class->set_trace_clearance_class(java::fr_num(default_class->get_trace_clearance_class()));
    return java::narrow<rules::NetClass*>(new_class);
}

rules::NetClass* BoardRules::append_net_class(QString p_name) {
    rules::NetClass* found_class = java::narrow<rules::NetClass*>(this->net_classes->get(p_name));
    if ((!java::fr_eq(found_class, nullptr))) {
        return java::narrow<rules::NetClass*>(found_class);
    }
    rules::NetClass* new_class = java::narrow<rules::NetClass*>(this->net_classes->append(p_name, this->layer_structure, this->clearance_matrix));
    rules::NetClass* default_class = java::narrow<rules::NetClass*>(this->net_classes->get(0));
    (java::fr_assign(new_class->default_item_clearance_classes, new rules::DefaultItemClearanceClasses(default_class->default_item_clearance_classes)));
    new_class->set_via_rule(java::narrow<rules::ViaRule*>(default_class->get_via_rule()));
    new_class->set_trace_half_width(java::fr_num(default_class->get_trace_half_width(java::fr_num(0))));
    new_class->set_trace_clearance_class(java::fr_num(default_class->get_trace_clearance_class()));
    return java::narrow<rules::NetClass*>(new_class);
}

rules::ViaRule* BoardRules::get_default_via_rule() {
    if (this->via_rules->isEmpty()) {
        return nullptr;
    }
    return java::narrow<rules::ViaRule*>(this->via_rules->get(0));
}

rules::ViaRule* BoardRules::get_via_rule(QString p_name) {
    for (auto* fr_fe_curr_rule : java::iterate(this->via_rules)) {
        rules::ViaRule* curr_rule = java::narrow<rules::ViaRule*>(fr_fe_curr_rule);
{
        if (((curr_rule->name) == (p_name))) {
            return java::narrow<rules::ViaRule*>(curr_rule);
        }
    }
    }
    return nullptr;
}

void BoardRules::change_clearance_class_no(int32_t p_from_no, int32_t p_to_no, java::util::Collection<board::Item*>* p_board_items) {
    for (auto* fr_fe_curr_item : java::iterate(p_board_items)) {
        board::Item* curr_item = java::narrow<board::Item*>(fr_fe_curr_item);
{
        if (java::fr_eq(curr_item->clearance_class_no(), p_from_no)) {
            curr_item->set_clearance_class_no(java::fr_num(p_to_no));
        }
    }
    }
    for (int32_t i = 0; (java::fr_cmp(i, this->net_classes->count()) < 0); ++i) {
        rules::NetClass* curr_net_class = java::narrow<rules::NetClass*>(this->net_classes->get(i));
        if (java::fr_eq(curr_net_class->get_trace_clearance_class(), p_from_no)) {
            curr_net_class->set_trace_clearance_class(java::fr_num(p_to_no));
        }
        for (auto* fr_fe_curr_item_class : java::iterate(rules::DefaultItemClearanceClasses_ItemClass::values())) {
            rules::DefaultItemClearanceClasses_ItemClass* curr_item_class = java::narrow<rules::DefaultItemClearanceClasses_ItemClass*>(fr_fe_curr_item_class);
{
            if (java::fr_eq(curr_net_class->default_item_clearance_classes->get(java::narrow<rules::DefaultItemClearanceClasses_ItemClass*>(curr_item_class)), p_from_no)) {
                curr_net_class->default_item_clearance_classes->set(java::narrow<rules::DefaultItemClearanceClasses_ItemClass*>(curr_item_class), java::fr_num(p_to_no));
            }
        }
        }
    }
    for (int32_t i = 0; (java::fr_cmp(i, this->via_infos->count()) < 0); ++i) {
        rules::ViaInfo* curr_via = java::narrow<rules::ViaInfo*>(this->via_infos->get(i));
        if (java::fr_eq(curr_via->get_clearance_class(), p_from_no)) {
            curr_via->set_clearance_class(java::fr_num(p_to_no));
        }
    }
}

bool BoardRules::remove_clearance_class(int32_t p_index, java::util::Collection<board::Item*>* p_board_items) {
    for (auto* fr_fe_curr_item : java::iterate(p_board_items)) {
        board::Item* curr_item = java::narrow<board::Item*>(fr_fe_curr_item);
{
        if (java::fr_eq(curr_item->clearance_class_no(), p_index)) {
            return java::fr_num(false);
        }
    }
    }
    for (int32_t i = 0; (java::fr_cmp(i, this->net_classes->count()) < 0); ++i) {
        rules::NetClass* curr_net_class = java::narrow<rules::NetClass*>(this->net_classes->get(i));
        if (java::fr_eq(curr_net_class->get_trace_clearance_class(), p_index)) {
            return java::fr_num(false);
        }
        for (auto* fr_fe_curr_item_class : java::iterate(rules::DefaultItemClearanceClasses_ItemClass::values())) {
            rules::DefaultItemClearanceClasses_ItemClass* curr_item_class = java::narrow<rules::DefaultItemClearanceClasses_ItemClass*>(fr_fe_curr_item_class);
{
            if (java::fr_eq(curr_net_class->default_item_clearance_classes->get(java::narrow<rules::DefaultItemClearanceClasses_ItemClass*>(curr_item_class)), p_index)) {
                return java::fr_num(false);
            }
        }
        }
    }
    for (int32_t i = 0; (java::fr_cmp(i, this->via_infos->count()) < 0); ++i) {
        rules::ViaInfo* curr_via = java::narrow<rules::ViaInfo*>(this->via_infos->get(i));
        if (java::fr_eq(curr_via->get_clearance_class(), p_index)) {
            return java::fr_num(false);
        }
    }
    for (auto* fr_fe_curr_item : java::iterate(p_board_items)) {
        board::Item* curr_item = java::narrow<board::Item*>(fr_fe_curr_item);
{
        if ((java::fr_cmp(curr_item->clearance_class_no(), p_index) > 0)) {
            curr_item->set_clearance_class_no(java::fr_num((curr_item->clearance_class_no() - 1)));
        }
    }
    }
    for (int32_t i = 0; (java::fr_cmp(i, this->net_classes->count()) < 0); ++i) {
        rules::NetClass* curr_net_class = java::narrow<rules::NetClass*>(this->net_classes->get(i));
        if ((java::fr_cmp(curr_net_class->get_trace_clearance_class(), p_index) > 0)) {
            curr_net_class->set_trace_clearance_class(java::fr_num((curr_net_class->get_trace_clearance_class() - 1)));
        }
        for (auto* fr_fe_curr_item_class : java::iterate(rules::DefaultItemClearanceClasses_ItemClass::values())) {
            rules::DefaultItemClearanceClasses_ItemClass* curr_item_class = java::narrow<rules::DefaultItemClearanceClasses_ItemClass*>(fr_fe_curr_item_class);
{
            int32_t curr_class_no = java::fr_num(curr_net_class->default_item_clearance_classes->get(java::narrow<rules::DefaultItemClearanceClasses_ItemClass*>(curr_item_class)));
            if ((java::fr_cmp(curr_class_no, p_index) > 0)) {
                curr_net_class->default_item_clearance_classes->set(java::narrow<rules::DefaultItemClearanceClasses_ItemClass*>(curr_item_class), java::fr_num((curr_class_no - 1)));
            }
        }
        }
    }
    for (int32_t i = 0; (java::fr_cmp(i, this->via_infos->count()) < 0); ++i) {
        rules::ViaInfo* curr_via = java::narrow<rules::ViaInfo*>(this->via_infos->get(i));
        if ((java::fr_cmp(curr_via->get_clearance_class(), p_index) > 0)) {
            curr_via->set_clearance_class(java::fr_num((curr_via->get_clearance_class() - 1)));
        }
    }
    this->clearance_matrix->remove_class(java::fr_num(p_index));
    return java::fr_num(true);
}

double BoardRules::get_pin_edge_to_turn_dist() {
    return java::fr_num(this->pin_edge_to_turn_dist);
}

void BoardRules::set_pin_edge_to_turn_dist(double p_value) {
    (java::fr_assign(this->pin_edge_to_turn_dist, p_value));
}

void BoardRules::set_ignore_conduction(bool p_value) {
    (java::fr_assign(this->ignore_conduction, p_value));
}

bool BoardRules::get_ignore_conduction() {
    return java::fr_num(this->ignore_conduction);
}

board::AngleRestriction* BoardRules::get_trace_angle_restriction() {
    return java::narrow<board::AngleRestriction*>(this->trace_angle_restriction);
}

void BoardRules::set_trace_angle_restriction(board::AngleRestriction* p_angle_restriction) {
    (java::fr_assign(this->trace_angle_restriction, p_angle_restriction));
}

void BoardRules::set_slow_autoroute_algorithm(bool p_value) {
    (java::fr_assign(this->slow_autoroute_algorithm, p_value));
}

bool BoardRules::get_slow_autoroute_algorithm() {
    return java::fr_num(this->slow_autoroute_algorithm);
}

double BoardRules::get_default_via_diameter() {
    rules::ViaRule* default_via_rule = java::narrow<rules::ViaRule*>(this->get_default_via_rule());
    if (java::fr_eq(default_via_rule, nullptr)) {
        return java::fr_num(0);
    }
    if ((java::fr_cmp(default_via_rule->via_count(), 0) <= 0)) {
        return java::fr_num(0);
    }
    library::Padstack* via_padstack = java::narrow<library::Padstack*>(default_via_rule->get_via(java::fr_num(0))->get_padstack());
    geometry::planar::ConvexShape* curr_shape = java::narrow<geometry::planar::ConvexShape*>(via_padstack->get_shape(java::fr_num(via_padstack->from_layer())));
    double result = java::fr_num(curr_shape->max_width());
    (java::fr_assign(curr_shape, via_padstack->get_shape(java::fr_num(via_padstack->to_layer()))));
    (java::fr_assign(result, java::lang::Math::max(result, curr_shape->max_width())));
    return java::fr_num(result);
}

void BoardRules::writeObject(java::io::ObjectOutputStream* p_stream) {
    p_stream->defaultWriteObject();
    p_stream->writeInt(trace_angle_restriction->get_no());
}

void BoardRules::readObject(java::io::ObjectInputStream* p_stream) {
    p_stream->defaultReadObject();
    int32_t snap_angle_no = java::fr_num(p_stream->readInt());
    (java::fr_assign(this->trace_angle_restriction, board::AngleRestriction::arr[snap_angle_no]));
}
}
