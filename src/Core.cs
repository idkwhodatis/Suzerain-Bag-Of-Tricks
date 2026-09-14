using MelonLoader;
using SuzerainModdingKit;
using UnityEngine.InputSystem;

[assembly:MelonInfo(typeof(BagOfTricks.Core),"BagOfTricks","0.1.0","idkwhodatis",null)]
[assembly:MelonGame("Torpor Games","Suzerain")]

namespace BagOfTricks;
internal sealed class Core:MelonMod
{
    internal static Core Instance=null!;
    internal CheatMenu menu=new CheatMenu();
    public override void OnInitializeMelon()
    {
        Instance=this;
        LoggerInstance.Msg("BagOfTricks 0.1.0 initialized (F10 toggles menu).");
    }
    public override void OnUpdate()
    {
        var kb=Keyboard.current;
        if(kb!=null&&kb.f10Key.wasPressedThisFrame)menu.visible=!menu.visible;
        Dump.onUpdate();
    }
    public override void OnGUI()
    {
        if(menu.visible)menu.draw();
    }
}
