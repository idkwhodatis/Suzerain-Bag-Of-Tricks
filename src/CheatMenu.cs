using MelonLoader;
using SuzerainModdingKit;
using UnityEngine;
using UnityEngine.InputSystem;

namespace BagOfTricks;
// Live cheat menu (IMGUI). Rows generated from Keys.Typed (full catalog).
// Reads/writes through SMK Variables (DialogueLua.Get/SetVariable).
internal sealed class CheatMenu
{
    internal bool visible=false;
    internal string drawError="";
    internal string search="";
    internal Vector2 scroll=new Vector2(0,0);
    internal Rect win=new Rect(20,20,380,560);
    internal static string shortName(string key)
    {
        int i=key.LastIndexOf('.');
        return i>=0?key.Substring(i+1):key;
    }
    internal void draw()
    {
        GUI.Box(win,"");
        Rect bar=new Rect(win.x,win.y,win.width,20);
        GUI.Box(bar,"BagOfTricks (F10)");
        dragBar(bar);
        GUILayout.BeginArea(new Rect(win.x+4,win.y+24,win.width-8,win.height-28));
        try{drawBody();}
        catch(System.Exception ex)
        {
            if(drawError==""){drawError=ex.GetType().Name+": "+ex.Message;Melon<Core>.Logger.Error(drawError);}
            GUILayout.Label(drawError);
        }
        GUILayout.EndArea();
    }
    internal void dragBar(Rect bar)
    {
        var m=Mouse.current;
        if(m==null)return;
        Vector2 mp=m.position.ReadValue();
        mp.y=Screen.height-mp.y;
        if(m.leftButton.wasPressedThisFrame&&bar.Contains(mp)){dragging=true;dragOff=new Vector2(win.x-mp.x,win.y-mp.y);}
        if(m.leftButton.isPressed==false)dragging=false;
        if(dragging){win.x=mp.x+dragOff.x;win.y=mp.y+dragOff.y;}
    }
    internal bool dragging=false;
    internal Vector2 dragOff=new Vector2(0,0);
    internal void drawBody()
    {
        string head=GameState.IsGameActive
            ?GameState.CurrentStoryPackName+" T"+GameState.CurrentTurnNum+" S"+GameState.CurrentStepNum
            :"no campaign loaded";
        GUILayout.Label(head);
        if(Dump.lastResult.Length>0)GUILayout.Label(Dump.lastResult);
        GUILayout.Label("F9 = dump all keys (see log + UserData)");
        GUILayout.BeginHorizontal();
        GUILayout.Label("Search",GUILayout.Width(50));
        search=GUILayout.TextField(search);
        GUILayout.EndHorizontal();
        GUILayout.BeginHorizontal();
        if(GUILayout.Button("Max Sordland"))maxSordland();
        if(GUILayout.Button("Max Rizia"))maxRizia();
        GUILayout.EndHorizontal();
        scroll=GUILayout.BeginScrollView(scroll);
        string q=search.ToLowerInvariant();
        int shown=0;
        int skipped=0;
        foreach(var e in Keys.Typed)
        {
            string label=shortName(e.name);
            if(search.Length>0&&label.ToLowerInvariant().Contains(q)==false
                &&e.name.ToLowerInvariant().Contains(q)==false)continue;
            if(shown>=400){skipped++;continue;}
            shown++;
            GUILayout.BeginHorizontal();
            GUILayout.Label(label,GUILayout.Width(150));
            try
            {
                if(e.isBool)drawBool(e.name);
                else drawInt(e.name);
            }
            catch{GUILayout.Label("ERR",GUILayout.Width(80));}
            GUILayout.EndHorizontal();
        }
        if(skipped>0)GUILayout.Label("+"+skipped+" more (refine search)");
        GUILayout.EndScrollView();
    }
    internal void drawInt(string key)
    {
        int v=Variables.GetInt(key);
        GUILayout.Label(v.ToString(),GUILayout.Width(50));
        if(GUILayout.Button("-",GUILayout.Width(30)))Variables.Set(key,v-1);
        if(GUILayout.Button("+",GUILayout.Width(30)))Variables.Set(key,v+1);
    }
    internal void drawBool(string key)
    {
        bool v=Variables.GetBool(key);
        if(GUILayout.Button(v?"ON":"OFF",GUILayout.Width(80)))Variables.Set(key,!v);
    }
    internal void maxSordland()
    {
        Variables.Set("BaseGame.GovernmentBudget",Variables.GetInt("BaseGame.Sordland_HUDStat_GovernmentBudget_Max"));
        Variables.Set("BaseGame.PersonalWealth",Variables.GetInt("BaseGame.Sordland_HUDStat_PersonalWealth_Max"));
    }
    internal void maxRizia()
    {
        Variables.Set("RiziaDLC.Resources_Budget",Variables.GetInt("RiziaDLC.Rizia_HUDStat_Budget_Max"));
        Variables.Set("RiziaDLC.Resources_Authority",Variables.GetInt("RiziaDLC.Rizia_HUDStat_Authority_Max"));
        Variables.Set("RiziaDLC.Resources_Energy",Variables.GetInt("RiziaDLC.Rizia_HUDStat_Energy_Max"));
    }
}
