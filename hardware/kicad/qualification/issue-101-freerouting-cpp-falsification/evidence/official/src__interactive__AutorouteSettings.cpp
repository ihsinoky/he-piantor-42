#include "interactive/AutorouteSettings.h"
#include "interactive/fr_package.h"
#include "board/RoutingBoard.h"
#include "autoroute/AutorouteControl.h"
#include "board/RoutingBoard.h"
#include "autoroute/AutorouteControl.h"
#include "autoroute/AutorouteControl.h"
#include "rules/BoardRules.h"
#include "rules/ClearanceMatrix.h"
#include "rules/Nets.h"
#include "rules/Net.h"
#include "rules/NetClass.h"
#include "board/BoardObservers.h"
#include "board/ItemSelectionFilter.h"
#include "library/Padstack.h"
#include "rules/ViaInfos.h"
#include "rules/NetClasses.h"
#include "geometry/planar/IntPoint.h"
#include "geometry/planar/IntBox.h"
#include "geometry/planar/FloatPoint.h"
#include "board/Layer.h"
#include "board/BasicBoard.h"
#include "board/LayerStructure.h"
#include "board/Components.h"
#include "board/Communication.h"
#include "library/BoardLibrary.h"
#include "library/Padstacks.h"
#include "library/Packages.h"
#include "library/Package.h"
#include "library/LogicalParts.h"
#include "library/LogicalPart.h"
#include "board/RoutingBoard.h"
#include "board/FixedState.h"
#include "board/SearchTreeManager.h"
#include "board/ShapeSearchTree.h"
#include "board/ConductionArea.h"
#include "board/Item.h"
#include "geometry/planar/Polyline.h"
#include "geometry/planar/Direction.h"
#include "geometry/planar/IntPoint.h"
#include "rules/ViaInfo.h"
#include "rules/ViaRule.h"
#include "interactive/BoardHandling.h"
#include "interactive/Settings.h"
#include "interactive/AutorouteSettings.h"
#include "interactive/ScreenMessages.h"
#include "interactive/RatsNest.h"
#include "board/CoordinateTransform.h"
#include "boardgraphics/GraphicsContext.h"
#include "gui/BoardPanel.h"
#include "gui/BoardFrame.h"
#include "boardgraphics/CoordinateTransform.h"
#include "designformats/specctra/CoordinateTransform.h"
#include "datastructures/IndentFileWriter.h"
#include "datastructures/IdentifierType.h"

namespace interactive {
AutorouteSettings::AutorouteSettings(int32_t p_layer_count) {
    (java::fr_assign(this->layer_active_arr, java::Array<bool>(p_layer_count)));
    (java::fr_assign(this->preferred_direction_is_horizontal_arr, java::Array<bool>(p_layer_count)));
    (java::fr_assign(this->preferred_direction_trace_cost_arr, java::Array<double>(p_layer_count)));
    (java::fr_assign(this->against_preferred_direction_trace_cost_arr, java::Array<double>(p_layer_count)));
}

AutorouteSettings::AutorouteSettings(board::RoutingBoard* p_board) : AutorouteSettings(p_board->get_layer_count()) {
    (java::fr_assign(this->start_ripup_costs, 100));
    (java::fr_assign(this->start_pass_no, 1));
    (java::fr_assign(this->vias_allowed, true));
    (java::fr_assign(this->with_fanout, false));
    (java::fr_assign(this->with_autoroute, true));
    (java::fr_assign(this->with_postroute, true));
    (java::fr_assign(this->via_costs, 50));
    (java::fr_assign(this->plane_via_costs, 5));
    double horizontal_width = java::fr_num(p_board->bounding_box->width());
    double vertical_width = java::fr_num(p_board->bounding_box->height());
    int32_t layer_count = java::fr_num(p_board->get_layer_count());
    double horizontal_add_costs_against_preferred_dir = java::fr_num((0.1 * java::lang::Math::round(((10 * horizontal_width) / vertical_width))));
    double vertical_add_costs_against_preferred_dir = java::fr_num((0.1 * java::lang::Math::round(((10 * vertical_width) / horizontal_width))));
    bool curr_preferred_direction_is_horizontal = java::fr_num((java::fr_cmp(horizontal_width, vertical_width) < 0));
    for (int32_t i = 0; (java::fr_cmp(i, layer_count) < 0); ++i) {
        (java::fr_assign(this->layer_active_arr[i], p_board->layer_structure->arr[i]->is_signal));
        if (p_board->layer_structure->arr[i]->is_signal) {
            (java::fr_assign(curr_preferred_direction_is_horizontal, !curr_preferred_direction_is_horizontal));
        }
        (java::fr_assign(this->preferred_direction_is_horizontal_arr[i], curr_preferred_direction_is_horizontal));
        (java::fr_assign(this->preferred_direction_trace_cost_arr[i], 1));
        (java::fr_assign(this->against_preferred_direction_trace_cost_arr[i], 1));
        if (curr_preferred_direction_is_horizontal) {
            (this->against_preferred_direction_trace_cost_arr[i] += horizontal_add_costs_against_preferred_dir);
        } else {
            (this->against_preferred_direction_trace_cost_arr[i] += vertical_add_costs_against_preferred_dir);
        }
    }
    int32_t signal_layer_count = java::fr_num(p_board->layer_structure->signal_layer_count());
    if ((java::fr_cmp(signal_layer_count, 2) > 0)) {
        double outer_add_costs = java::fr_num((0.2 * signal_layer_count));
        (this->preferred_direction_trace_cost_arr[0] += outer_add_costs);
        (this->preferred_direction_trace_cost_arr[(layer_count - 1)] += outer_add_costs);
        (this->against_preferred_direction_trace_cost_arr[0] += outer_add_costs);
        (this->against_preferred_direction_trace_cost_arr[(layer_count - 1)] += outer_add_costs);
    }
}

AutorouteSettings::AutorouteSettings(interactive::AutorouteSettings* p_settings) {
    (java::fr_assign(this->start_ripup_costs, p_settings->start_ripup_costs));
    (java::fr_assign(this->start_pass_no, p_settings->start_pass_no));
    (java::fr_assign(this->via_costs, p_settings->via_costs));
    (java::fr_assign(this->plane_via_costs, p_settings->plane_via_costs));
    (java::fr_assign(this->layer_active_arr, java::Array<bool>(p_settings->layer_active_arr.length)));
    java::arraycopy(p_settings->layer_active_arr, 0, this->layer_active_arr, 0, layer_active_arr.length);
    (java::fr_assign(this->preferred_direction_is_horizontal_arr, java::Array<bool>(p_settings->preferred_direction_is_horizontal_arr.length)));
    java::arraycopy(p_settings->preferred_direction_is_horizontal_arr, 0, this->preferred_direction_is_horizontal_arr, 0, preferred_direction_is_horizontal_arr.length);
    (java::fr_assign(this->preferred_direction_trace_cost_arr, java::Array<double>(p_settings->preferred_direction_trace_cost_arr.length)));
    java::arraycopy(p_settings->preferred_direction_trace_cost_arr, 0, this->preferred_direction_trace_cost_arr, 0, preferred_direction_trace_cost_arr.length);
    (java::fr_assign(this->against_preferred_direction_trace_cost_arr, java::Array<double>(p_settings->against_preferred_direction_trace_cost_arr.length)));
    java::arraycopy(p_settings->against_preferred_direction_trace_cost_arr, 0, this->against_preferred_direction_trace_cost_arr, 0, against_preferred_direction_trace_cost_arr.length);
}

void AutorouteSettings::set_start_ripup_costs(int32_t p_value) {
    (java::fr_assign(this->start_ripup_costs, java::lang::Math::max(p_value, 1)));
}

int32_t AutorouteSettings::get_start_ripup_costs() {
    return java::fr_num(this->start_ripup_costs);
}

void AutorouteSettings::set_pass_no(int32_t p_value) {
    (java::fr_assign(this->start_pass_no, java::lang::Math::max(p_value, 1)));
    (java::fr_assign(this->start_pass_no, java::lang::Math::min(this->start_pass_no, 99)));
}

int32_t AutorouteSettings::get_pass_no() {
    return java::fr_num(this->start_pass_no);
}

void AutorouteSettings::increment_pass_no() {
    ++this->start_pass_no;
}

void AutorouteSettings::set_with_fanout(bool p_value) {
    (java::fr_assign(this->with_fanout, p_value));
}

bool AutorouteSettings::get_with_fanout() {
    return java::fr_num(this->with_fanout);
}

void AutorouteSettings::set_with_autoroute(bool p_value) {
    (java::fr_assign(this->with_autoroute, p_value));
}

bool AutorouteSettings::get_with_autoroute() {
    return java::fr_num(this->with_autoroute);
}

void AutorouteSettings::set_with_postroute(bool p_value) {
    (java::fr_assign(this->with_postroute, p_value));
}

bool AutorouteSettings::get_with_postroute() {
    return java::fr_num(this->with_postroute);
}

void AutorouteSettings::set_vias_allowed(bool p_value) {
    (java::fr_assign(this->vias_allowed, p_value));
}

bool AutorouteSettings::get_vias_allowed() {
    return java::fr_num(this->vias_allowed);
}

void AutorouteSettings::set_via_costs(int32_t p_value) {
    (java::fr_assign(this->via_costs, java::lang::Math::max(p_value, 1)));
}

int32_t AutorouteSettings::get_via_costs() {
    return java::fr_num(this->via_costs);
}

void AutorouteSettings::set_plane_via_costs(int32_t p_value) {
    (java::fr_assign(this->plane_via_costs, java::lang::Math::max(p_value, 1)));
}

int32_t AutorouteSettings::get_plane_via_costs() {
    return java::fr_num(this->plane_via_costs);
}

void AutorouteSettings::set_layer_active(int32_t p_layer, bool p_value) {
    if (((java::fr_cmp(p_layer, 0) < 0) || (java::fr_cmp(p_layer, layer_active_arr.length) >= 0))) {
        java::lang::System::out.println(QString::fromUtf8("\x41\x75\x74\x6f\x72\x6f\x75\x74\x65\x53\x65\x74\x74\x69\x6e\x67\x73\x2e\x73\x65\x74\x5f\x6c\x61\x79\x65\x72\x5f\x61\x63\x74\x69\x76\x65\x3a\x20\x70\x5f\x6c\x61\x79\x65\x72\x20\x6f\x75\x74\x20\x6f\x66\x20\x72\x61\x6e\x67\x65", 56));
        return;
    }
    (java::fr_assign(this->layer_active_arr[p_layer], p_value));
}

bool AutorouteSettings::get_layer_active(int32_t p_layer) {
    if (((java::fr_cmp(p_layer, 0) < 0) || (java::fr_cmp(p_layer, layer_active_arr.length) >= 0))) {
        java::lang::System::out.println(QString::fromUtf8("\x41\x75\x74\x6f\x72\x6f\x75\x74\x65\x53\x65\x74\x74\x69\x6e\x67\x73\x2e\x67\x65\x74\x5f\x6c\x61\x79\x65\x72\x5f\x61\x63\x74\x69\x76\x65\x3a\x20\x70\x5f\x6c\x61\x79\x65\x72\x20\x6f\x75\x74\x20\x6f\x66\x20\x72\x61\x6e\x67\x65", 56));
        return java::fr_num(false);
    }
    return java::fr_num(this->layer_active_arr[p_layer]);
}

void AutorouteSettings::set_preferred_direction_is_horizontal(int32_t p_layer, bool p_value) {
    if (((java::fr_cmp(p_layer, 0) < 0) || (java::fr_cmp(p_layer, layer_active_arr.length) >= 0))) {
        java::lang::System::out.println(QString::fromUtf8("\x41\x75\x74\x6f\x72\x6f\x75\x74\x65\x53\x65\x74\x74\x69\x6e\x67\x73\x2e\x73\x65\x74\x5f\x70\x72\x65\x66\x65\x72\x72\x65\x64\x5f\x64\x69\x72\x65\x63\x74\x69\x6f\x6e\x5f\x69\x73\x5f\x68\x6f\x72\x69\x7a\x6f\x6e\x74\x61\x6c\x3a\x20\x70\x5f\x6c\x61\x79\x65\x72\x20\x6f\x75\x74\x20\x6f\x66\x20\x72\x61\x6e\x67\x65", 77));
        return;
    }
    (java::fr_assign(this->preferred_direction_is_horizontal_arr[p_layer], p_value));
}

bool AutorouteSettings::get_preferred_direction_is_horizontal(int32_t p_layer) {
    if (((java::fr_cmp(p_layer, 0) < 0) || (java::fr_cmp(p_layer, layer_active_arr.length) >= 0))) {
        java::lang::System::out.println(QString::fromUtf8("\x41\x75\x74\x6f\x72\x6f\x75\x74\x65\x53\x65\x74\x74\x69\x6e\x67\x73\x2e\x67\x65\x74\x5f\x70\x72\x65\x66\x65\x72\x72\x65\x64\x5f\x64\x69\x72\x65\x63\x74\x69\x6f\x6e\x5f\x69\x73\x5f\x68\x6f\x72\x69\x7a\x6f\x6e\x74\x61\x6c\x3a\x20\x70\x5f\x6c\x61\x79\x65\x72\x20\x6f\x75\x74\x20\x6f\x66\x20\x72\x61\x6e\x67\x65", 77));
        return java::fr_num(false);
    }
    return java::fr_num(this->preferred_direction_is_horizontal_arr[p_layer]);
}

void AutorouteSettings::set_preferred_direction_trace_costs(int32_t p_layer, double p_value) {
    if (((java::fr_cmp(p_layer, 0) < 0) || (java::fr_cmp(p_layer, layer_active_arr.length) >= 0))) {
        java::lang::System::out.println(QString::fromUtf8("\x41\x75\x74\x6f\x72\x6f\x75\x74\x65\x53\x65\x74\x74\x69\x6e\x67\x73\x2e\x73\x65\x74\x5f\x70\x72\x65\x66\x65\x72\x72\x65\x64\x5f\x64\x69\x72\x65\x63\x74\x69\x6f\x6e\x5f\x74\x72\x61\x63\x65\x5f\x63\x6f\x73\x74\x73\x3a\x20\x70\x5f\x6c\x61\x79\x65\x72\x20\x6f\x75\x74\x20\x6f\x66\x20\x72\x61\x6e\x67\x65", 75));
        return;
    }
    (java::fr_assign(this->preferred_direction_trace_cost_arr[p_layer], java::lang::Math::max(p_value, 0.1)));
}

double AutorouteSettings::get_preferred_direction_trace_costs(int32_t p_layer) {
    if (((java::fr_cmp(p_layer, 0) < 0) || (java::fr_cmp(p_layer, layer_active_arr.length) >= 0))) {
        java::lang::System::out.println(QString::fromUtf8("\x41\x75\x74\x6f\x72\x6f\x75\x74\x65\x53\x65\x74\x74\x69\x6e\x67\x73\x2e\x67\x65\x74\x5f\x70\x72\x65\x66\x65\x72\x72\x65\x64\x5f\x64\x69\x72\x65\x63\x74\x69\x6f\x6e\x5f\x74\x72\x61\x63\x65\x5f\x63\x6f\x73\x74\x73\x3a\x20\x70\x5f\x6c\x61\x79\x65\x72\x20\x6f\x75\x74\x20\x6f\x66\x20\x72\x61\x6e\x67\x65", 75));
        return java::fr_num(0);
    }
    return java::fr_num(this->preferred_direction_trace_cost_arr[p_layer]);
}

double AutorouteSettings::get_against_preferred_direction_trace_costs(int32_t p_layer) {
    if (((java::fr_cmp(p_layer, 0) < 0) || (java::fr_cmp(p_layer, layer_active_arr.length) >= 0))) {
        java::lang::System::out.println(QString::fromUtf8("\x41\x75\x74\x6f\x72\x6f\x75\x74\x65\x53\x65\x74\x74\x69\x6e\x67\x73\x2e\x67\x65\x74\x5f\x61\x67\x61\x69\x6e\x73\x74\x5f\x70\x72\x65\x66\x65\x72\x72\x65\x64\x5f\x64\x69\x72\x65\x63\x74\x69\x6f\x6e\x5f\x74\x72\x61\x63\x65\x5f\x63\x6f\x73\x74\x73\x3a\x20\x70\x5f\x6c\x61\x79\x65\x72\x20\x6f\x75\x74\x20\x6f\x66\x20\x72\x61\x6e\x67\x65", 83));
        return java::fr_num(0);
    }
    return java::fr_num(this->against_preferred_direction_trace_cost_arr[p_layer]);
}

double AutorouteSettings::get_horizontal_trace_costs(int32_t p_layer) {
    if (((java::fr_cmp(p_layer, 0) < 0) || (java::fr_cmp(p_layer, layer_active_arr.length) >= 0))) {
        java::lang::System::out.println(QString::fromUtf8("\x41\x75\x74\x6f\x72\x6f\x75\x74\x65\x53\x65\x74\x74\x69\x6e\x67\x73\x2e\x67\x65\x74\x5f\x70\x72\x65\x66\x65\x72\x72\x65\x64\x5f\x64\x69\x72\x65\x63\x74\x69\x6f\x6e\x5f\x74\x72\x61\x63\x65\x5f\x63\x6f\x73\x74\x73\x3a\x20\x70\x5f\x6c\x61\x79\x65\x72\x20\x6f\x75\x74\x20\x6f\x66\x20\x72\x61\x6e\x67\x65", 75));
        return java::fr_num(0);
    }
    double result;
    if (this->preferred_direction_is_horizontal_arr[p_layer]) {
        (java::fr_assign(result, this->preferred_direction_trace_cost_arr[p_layer]));
    } else {
        (java::fr_assign(result, this->against_preferred_direction_trace_cost_arr[p_layer]));
    }
    return java::fr_num(result);
}

void AutorouteSettings::set_against_preferred_direction_trace_costs(int32_t p_layer, double p_value) {
    if (((java::fr_cmp(p_layer, 0) < 0) || (java::fr_cmp(p_layer, layer_active_arr.length) >= 0))) {
        java::lang::System::out.println(QString::fromUtf8("\x41\x75\x74\x6f\x72\x6f\x75\x74\x65\x53\x65\x74\x74\x69\x6e\x67\x73\x2e\x73\x65\x74\x5f\x61\x67\x61\x69\x6e\x73\x74\x5f\x70\x72\x65\x66\x65\x72\x72\x65\x64\x5f\x64\x69\x72\x65\x63\x74\x69\x6f\x6e\x5f\x74\x72\x61\x63\x65\x5f\x63\x6f\x73\x74\x73\x3a\x20\x70\x5f\x6c\x61\x79\x65\x72\x20\x6f\x75\x74\x20\x6f\x66\x20\x72\x61\x6e\x67\x65", 83));
        return;
    }
    (java::fr_assign(this->against_preferred_direction_trace_cost_arr[p_layer], java::lang::Math::max(p_value, 0.1)));
}

double AutorouteSettings::get_vertical_trace_costs(int32_t p_layer) {
    if (((java::fr_cmp(p_layer, 0) < 0) || (java::fr_cmp(p_layer, layer_active_arr.length) >= 0))) {
        java::lang::System::out.println(QString::fromUtf8("\x41\x75\x74\x6f\x72\x6f\x75\x74\x65\x53\x65\x74\x74\x69\x6e\x67\x73\x2e\x67\x65\x74\x5f\x61\x67\x61\x69\x6e\x73\x74\x5f\x70\x72\x65\x66\x65\x72\x72\x65\x64\x5f\x64\x69\x72\x65\x63\x74\x69\x6f\x6e\x5f\x74\x72\x61\x63\x65\x5f\x63\x6f\x73\x74\x73\x3a\x20\x70\x5f\x6c\x61\x79\x65\x72\x20\x6f\x75\x74\x20\x6f\x66\x20\x72\x61\x6e\x67\x65", 83));
        return java::fr_num(0);
    }
    double result;
    if (this->preferred_direction_is_horizontal_arr[p_layer]) {
        (java::fr_assign(result, this->against_preferred_direction_trace_cost_arr[p_layer]));
    } else {
        (java::fr_assign(result, this->preferred_direction_trace_cost_arr[p_layer]));
    }
    return java::fr_num(result);
}

java::Array<autoroute::AutorouteControl_ExpansionCostFactor*> AutorouteSettings::get_trace_cost_arr() {
    java::Array<autoroute::AutorouteControl_ExpansionCostFactor*> result = java::Array<autoroute::AutorouteControl_ExpansionCostFactor*>(preferred_direction_trace_cost_arr.length);
    for (int32_t i = 0; (java::fr_cmp(i, result.length) < 0); ++i) {
        (java::fr_assign(result[i], new autoroute::AutorouteControl_ExpansionCostFactor(this->get_horizontal_trace_costs(java::fr_num(i)), this->get_vertical_trace_costs(java::fr_num(i)))));
    }
    return result;
}
}
