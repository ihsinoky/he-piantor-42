#include "interactive/BatchAutorouterThread.h"

#include "interactive/fr_package.h"
#include "geometry/planar/FloatPoint.h"
#include "geometry/planar/FloatLine.h"
#include "board/Unit.h"
#include "autoroute2/session.h"
#include "tests/Validate.h"
#include "board/AngleRestriction.h"
#include "board/Unit.h"
#include "board/TestLevel.h"
#include "geometry/planar/FloatPoint.h"
#include "geometry/planar/FloatLine.h"
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
BatchAutorouterThread::BatchAutorouterThread(interactive::BoardHandling* p_board_handling) : interactive::InteractiveActionThread(p_board_handling) {
}

void BatchAutorouterThread::thread_action() {
    try {
    java::util::ResourceBundle resources = java::util::ResourceBundle::getBundle(QString::fromUtf8("\x69\x6e\x74\x65\x72\x61\x63\x74\x69\x76\x65\x2e\x72\x65\x73\x6f\x75\x72\x63\x65\x73\x2e\x49\x6e\x74\x65\x72\x61\x63\x74\x69\x76\x65\x53\x74\x61\x74\x65", 38), this->hdlg->get_locale());
    bool saved_board_read_only = java::fr_num(this->hdlg->is_board_read_only());
    this->hdlg->set_board_read_only(java::fr_num(true));
    bool ratsnest_hidden_before = java::fr_num(this->hdlg->get_ratsnest()->is_hidden());
    if (!ratsnest_hidden_before) {
        this->hdlg->get_ratsnest()->hide();
    }
    QString start_message = ((resources.getString(QString::fromUtf8("\x62\x61\x74\x63\x68\x5f\x61\x75\x74\x6f\x72\x6f\x75\x74\x65\x72", 16)) + QString::fromUtf8("\x20", 1)) + resources.getString(QString::fromUtf8("\x73\x74\x6f\x70\x5f\x6d\x65\x73\x73\x61\x67\x65", 12)));
    this->hdlg->screen_messages->set_status_message(start_message);
    autoroute2::run_session(this->hdlg, this);
    this->hdlg->set_board_read_only(java::fr_num(saved_board_read_only));
    this->hdlg->update_ratsnest();
    if (!ratsnest_hidden_before) {
        this->hdlg->get_ratsnest()->show();
    }
    this->hdlg->get_panel()->board_frame->refresh_windows();
    if ((java::fr_eq(this->hdlg->get_routing_board()->rules->get_trace_angle_restriction(), board::AngleRestriction::FORTYFIVE_DEGREE) && (!java::fr_eq(this->hdlg->get_routing_board()->get_test_level(), board::TestLevel::RELEASE_VERSION)))) {
        tests::Validate::multiple_of_45_degree(QString::fromUtf8("\x61\x66\x74\x65\x72\x20\x61\x75\x74\x6f\x72\x6f\x75\x74\x65\x3a\x20", 17), this->hdlg->get_routing_board());
    }
    } catch (java::lang::Exception* e) {
        std::cerr << "BatchAutorouterThread: "
                  << (e ? e->getMessage().toStdString() : "?") << "\n";
    } catch (const java::lang::Exception& e) {
        std::cerr << "BatchAutorouterThread: " << e.getMessage().toStdString() << "\n";
    }
}

void BatchAutorouterThread::draw(java::awt::Graphics* p_graphics) {
    autoroute2::Airline air = autoroute2::current_airline();
    if (air.valid) {
        java::Array<geometry::planar::FloatPoint*> draw_line = java::Array<geometry::planar::FloatPoint*>(2);
        (java::fr_assign(draw_line[0], new geometry::planar::FloatPoint(air.x0, air.y0)));
        (java::fr_assign(draw_line[1], new geometry::planar::FloatPoint(air.x1, air.y1)));
        java::awt::Color draw_color = this->hdlg->graphics_context->get_incomplete_color();
        double draw_width = java::fr_num(java::lang::Math::min((this->hdlg->get_routing_board()->communication->get_resolution(java::narrow<board::Unit*>(board::Unit::MIL)) * 3), 300));
        this->hdlg->graphics_context->draw(draw_line, java::fr_num(draw_width), java::fr_deref(draw_color), java::narrow<java::awt::Graphics*>(p_graphics), java::fr_num(1));
    }
}
}
