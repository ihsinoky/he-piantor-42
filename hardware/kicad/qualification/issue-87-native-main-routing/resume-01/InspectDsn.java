// Read-only calls into the fixed JAR's public headless API. Never route/mutate rules.
import java.io.*;
import java.nio.file.*;
import java.util.*;
import app.freerouting.interactive.HeadlessBoardManager;
import app.freerouting.core.RoutingJob;
import app.freerouting.board.*;
import app.freerouting.designforms.specctra.DsnFile;
import com.google.gson.GsonBuilder;

public class InspectDsn {
  static double[] box(BasicBoard board, app.freerouting.geometry.planar.IntBox box) {
    double[] a=board.communication.coordinate_transform.board_to_dsn(box);
    for(int i=0;i<a.length;i++)a[i]/=1000.0;
    return a;
  }
  public static void main(String[] args) throws Exception {
    var manager=new HeadlessBoardManager(Locale.ENGLISH,new RoutingJob());
    var result=manager.loadFromSpecctraDsn(new FileInputStream(args[0]),new BoardObserverAdaptor(),new ItemIdentificationNumberGenerator());
    if(result!=DsnFile.ReadResult.OK)throw new IllegalStateException("DSN load "+result);
    var board=manager.get_routing_board();
    var out=new LinkedHashMap<String,Object>();out.put("load_result",result.toString());out.put("units",board.communication.unit.toString());out.put("routing_launched",false);
    var matrix=new ArrayList<Object>();var cm=board.rules.clearance_matrix;
    for(int l=0;l<board.get_layer_count();l++)for(int i=0;i<cm.get_class_count();i++)for(int j=0;j<cm.get_class_count();j++) {
      var row=new LinkedHashMap<String,Object>();row.put("layer",board.layer_structure.arr[l].name);row.put("class_a",cm.get_name(i));row.put("class_b",cm.get_name(j));row.put("clearance_mm",board.communication.coordinate_transform.board_to_dsn(cm.get_value(i,j,l,false))/1000.0);matrix.add(row);
    }
    out.put("clearance_matrix",matrix);
    var pins=new ArrayList<Object>();
    for(var pin:board.get_pins()) {
      var row=new LinkedHashMap<String,Object>();row.put("component",pin.component_name());row.put("pin",pin.name());row.put("clearance_class",cm.get_name(pin.clearance_class_no()));
      var nets=new ArrayList<String>();for(int i=0;i<pin.net_count();i++)nets.add(board.rules.nets.get(pin.get_net_no(i)).name);row.put("nets",nets);
      var shapes=new ArrayList<Object>();for(int l=pin.first_layer();l<=pin.last_layer();l++)if(pin.is_on_layer(l)&&pin.get_shape(l)!=null) {
        var shape=new LinkedHashMap<String,Object>();shape.put("layer",board.layer_structure.arr[l].name);shape.put("bbox_dsn_mm",box(board,pin.get_shape(l).bounding_box()));shapes.add(shape);
      }
      row.put("shapes",shapes);pins.add(row);
    }
    out.put("pins",pins);
    var obstacles=new ArrayList<Object>();var traces=new ArrayList<Object>();
    for(var item:board.get_items()) {
      var row=new LinkedHashMap<String,Object>();row.put("kind",item.getClass().getSimpleName());row.put("component",item.component_name());row.put("clearance_class",cm.get_name(item.clearance_class_no()));row.put("bbox_dsn_mm",box(board,item.bounding_box()));row.put("first_layer",item.first_layer());row.put("last_layer",item.last_layer());row.put("fixed_state",item.get_fixed_state().toString());
      if(item instanceof ObstacleArea)obstacles.add(row);
      if(item instanceof Trace)traces.add(row);
    }
    out.put("obstacles",obstacles);out.put("traces",traces);
    var classes=new ArrayList<Object>();
    for(int i=0;i<board.rules.net_classes.count();i++) {
      var c=board.rules.net_classes.get(i);var row=new LinkedHashMap<String,Object>();row.put("name",c.get_name());row.put("trace_clearance_class",cm.get_name(c.get_trace_clearance_class()));
      var widths=new ArrayList<Double>();for(int l=0;l<board.get_layer_count();l++)widths.add(board.communication.coordinate_transform.board_to_dsn(2*c.get_trace_half_width(l))/1000.0);row.put("widths_mm",widths);classes.add(row);
    }
    out.put("netclasses",classes);out.put("components",board.components.count());out.put("layers",board.get_layer_count());
    Files.writeString(Path.of(args[1]),new GsonBuilder().setPrettyPrinting().create().toJson(out)+"\n");
    System.out.println("Read-only public API inspection: "+pins.size()+" pins, "+obstacles.size()+" obstacles; no routing");
  }
}
