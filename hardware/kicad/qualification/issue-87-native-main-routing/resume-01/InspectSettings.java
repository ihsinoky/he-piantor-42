// Public settings parser verification only; creates no routing job.
import app.freerouting.settings.GlobalSettings;
import com.google.gson.GsonBuilder;
import java.nio.file.*;
public class InspectSettings {
  public static void main(String[] args) throws Exception {
    var settings=new GlobalSettings();
    settings.applyCommandLineArguments(java.util.Arrays.copyOfRange(args,1,args.length));
    Files.writeString(Path.of(args[0]),new GsonBuilder().setPrettyPrinting().create().toJson(settings)+"\n");
    System.out.println("Public settings parse: passes="+settings.routerSettings.maxPasses+", routingThreads="+settings.routerSettings.maxThreads+", optimizerThreads="+settings.routerSettings.optimizer.maxThreads+", neckdown="+settings.routerSettings.automatic_neckdown+", gui="+settings.guiSettings.isEnabled+", optimizerEnabled="+settings.routerSettings.optimizer.enabled+", api="+settings.apiServerSettings.isEnabled);
    if(settings.routerSettings.maxPasses!=100||settings.routerSettings.maxThreads!=1||settings.routerSettings.optimizer.maxThreads!=0||settings.routerSettings.automatic_neckdown||settings.guiSettings.isEnabled||settings.apiServerSettings.isEnabled||settings.routerSettings.optimizer.enabled)throw new IllegalStateException("Settings mismatch");
  }
}
