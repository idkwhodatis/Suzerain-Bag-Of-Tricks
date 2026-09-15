using MelonLoader;
using SuzerainModdingKit;
using UnityEngine.InputSystem;

[assembly:MelonInfo(typeof(BagOfTricks.Core),"BagOfTricks",BagOfTricks.Core.Version,BagOfTricks.Core.Author,null)]
[assembly:MelonGame("Torpor Games","Suzerain")]

namespace BagOfTricks;
internal sealed class Core:MelonMod
{
    internal const string Version="0.1.0-alpha";
    internal const string Author="idkwhodatis";
    internal static Core Instance=null!;
    internal CheatMenu menu=new CheatMenu();
    internal MelonPreferences_Category prefs;
    internal MelonPreferences_Entry<string> langEntry;
    internal MelonPreferences_Entry<bool> experimentalEntry;
    internal System.DateTime bootedAt=System.DateTime.UtcNow;
    public override void OnInitializeMelon()
    {
        Instance=this;
        bootedAt=System.DateTime.UtcNow;
        prefs=MelonPreferences.CreateCategory("BagOfTricks");
        langEntry=prefs.CreateEntry<string>("Language","en");
        experimentalEntry=prefs.CreateEntry<bool>("ShowExperimental",false);
        Strings.current=langEntry.Value=="zh-Hans"?"zh-Hans":"en";
        LoggerInstance.Msg("BagOfTricks "+Version+" initialized (Ctrl+D toggles menu).");
        try{LoggerInstance.Msg($"data: groups={MenuData.Groups.Length} keys={Keys.Typed.Length} strings-en={Strings.en.Count}");}
        catch(System.Exception ex){LoggerInstance.Error("data check: "+ex.ToString());}
    }
    public override void OnUpdate()
    {
        if((System.DateTime.UtcNow-bootedAt).TotalSeconds<5)return;
        var kb=Keyboard.current;
        if(kb==null)return;
        if(kb.dKey.wasPressedThisFrame&&(kb.leftCtrlKey.isPressed||kb.rightCtrlKey.isPressed))
        {
            menu.visible=!menu.visible;
            LoggerInstance.Msg("menu "+(menu.visible?"shown":"hidden")+" by hotkey");
        }
        Dump.onUpdate();
    }
    public override void OnGUI()
    {
        if(menu.visible)menu.draw();
    }
}
