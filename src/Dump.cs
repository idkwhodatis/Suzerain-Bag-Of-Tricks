using Il2CppPixelCrushers.DialogueSystem;
using MelonLoader;
using SuzerainModdingKit;
using UnityEngine.InputSystem;

namespace BagOfTricks;
// F9: dump every known key (live presence + int/string casts) to UserData.
// Output feeds Agents/API.md confirmation (see src/README.md protocol).
internal static class Dump
{
    internal static string lastResult="";
    internal static void onUpdate()
    {
        var kb=Keyboard.current;
        if(kb!=null&&kb.f9Key.wasPressedThisFrame)run();
    }
    internal static void run()
    {
        string dir=System.IO.Path.Combine(MelonLoader.Utils.MelonEnvironment.UserDataDirectory,"BagOfTricks");
        System.IO.Directory.CreateDirectory(dir);
        string pack="menu";
        string turn="0";
        string step="0";
        if(GameState.IsGameActive){pack=GameState.CurrentStoryPackName;turn=GameState.CurrentTurnNum.ToString();step=GameState.CurrentStepNum.ToString();}
        string file=System.IO.Path.Combine(dir,"dump_"+pack+"_T"+turn+"_S"+step+"_"+System.DateTime.Now.ToString("yyyyMMdd_HHmmss")+".txt");
        int ok=0,absent=0,bad=0;
        using(var w=new System.IO.StreamWriter(file,false,System.Text.Encoding.UTF8))
        {
            w.WriteLine("key\texists\tint\tstr");
            foreach(var k in Keys.All)
            {
                bool ex=false;
                string iv="";
                string sv="";
                try
                {
                    ex=DialogueLua.DoesVariableExist(k);
                    if(ex){iv=Variables.GetInt(k).ToString();try{sv=Variables.GetString(k);}catch{sv="<str-err>";}ok++;}
                    else absent++;
                }
                catch{bad++;}
                w.WriteLine(k+"\t"+ex+"\t"+iv+"\t"+sv);
            }
        }
        Melon<Core>.Logger.Msg("BagOfTricks dump: "+ok+" live, "+absent+" absent, "+bad+" errors -> "+file);
        lastResult="F9 dump: "+ok+" live, "+absent+" absent, "+bad+" errors";
    }
}
