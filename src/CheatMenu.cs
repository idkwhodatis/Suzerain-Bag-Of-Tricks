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
    internal string expandedKey="";
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
        GUILayout.Label("Grouped (modify together):");
        string gq=search.ToLowerInvariant();
        foreach(var g in Groups.All)
        {
            if(search.Length>0&&g.name.ToLowerInvariant().Contains(gq)==false)continue;
            GUILayout.BeginHorizontal();
            GUILayout.Label(g.name,GUILayout.Width(150));
            try{drawGroup(g);}
            catch{GUILayout.Label("ERR",GUILayout.Width(80));}
            GUILayout.EndHorizontal();
        }
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
                drawWarnToggle(e.name);
            }
            catch{GUILayout.Label("ERR",GUILayout.Width(80));}
            GUILayout.EndHorizontal();
            if(expandedKey==e.name)drawWarnDetail(e.name);
        }
        if(skipped>0)GUILayout.Label("+"+skipped+" more (refine search)");
        GUILayout.EndScrollView();
    }
    internal void drawGroup(GroupDef g)
    {
        if(g.kind=="and")drawAnd(g.members);
        else if(g.kind=="inverse")drawInverse(g.members[0],g.members[1]);
        else if(g.kind=="compensating")drawCompensating(g.members[0],g.members[1]);
        else if(g.kind=="exclusive")drawExclusive(g);
        else GUILayout.Label("?",GUILayout.Width(80));
    }
    internal void drawAnd(string[] keys)
    {
        bool all=true;
        bool any=false;
        foreach(var k in keys)
        {
            bool v=Variables.GetBool(k);
            all=all&&v;
            any=any||v;
        }
        string label=all?"ON":(any?"MIX":"OFF");
        if(GUILayout.Button(label,GUILayout.Width(80)))
        {
            bool target=all==false;
            foreach(var k in keys)Variables.Set(k,target);
        }
    }
    internal void drawInverse(string winKey,string loseKey)
    {
        bool win=Variables.GetBool(winKey);
        if(GUILayout.Button(win?"WIN":"LOST",GUILayout.Width(80)))
        {
            Variables.Set(winKey,win==false);
            Variables.Set(loseKey,win);
        }
    }
    internal void drawExclusive(GroupDef g)
    {
        int cur=-1;
        for(int i=0;i<g.optNames.Length;i++)
        {
            bool match=true;
            foreach(var k in g.optKeys[i])match=match&&Variables.GetBool(k);
            if(match&&g.optKeys[i].Length>0){cur=i;break;}
        }
        string label=cur>=0?g.optNames[cur]:"—";
        GUILayout.Label(label,GUILayout.Width(80));
        if(GUILayout.Button("<",GUILayout.Width(30)))applyExclusive(g,cur-1);
        if(GUILayout.Button(">",GUILayout.Width(30)))applyExclusive(g,cur+1);
    }
    internal void applyExclusive(GroupDef g,int idx)
    {
        int n=g.optNames.Length;
        if(n==0)return;
        idx=((idx%n)+n)%n;
        foreach(var ks in g.optKeys)foreach(var k in ks)Variables.Set(k,false);
        foreach(var k in g.optKeys[idx])Variables.Set(k,true);
    }
    internal void drawCompensating(string totalKey,string baseKey)
    {
        int total=Variables.GetInt(totalKey);
        GUILayout.Label(total.ToString(),GUILayout.Width(50));
        if(GUILayout.Button("-",GUILayout.Width(30)))bumpCompensating(totalKey,baseKey,-1);
        if(GUILayout.Button("+",GUILayout.Width(30)))bumpCompensating(totalKey,baseKey,1);
    }
    internal void bumpCompensating(string totalKey,string baseKey,int delta)
    {
        int total=Variables.GetInt(totalKey);
        int bse=Variables.GetInt(baseKey);
        Variables.Set(totalKey,total+delta);
        Variables.Set(baseKey,bse+delta);
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
    internal void drawWarnToggle(string key)
    {
        var w=Warnings.Find(key);
        if(w==null)return;
        string mark=expandedKey==key?"-":"+";
        if(w.danger.Length>0&&dangerTripped(key))mark="!"+mark;
        if(GUILayout.Button(mark,GUILayout.Width(30)))expandedKey=expandedKey==key?"":key;
    }
    internal bool dangerTripped(string key)
    {
        try{return Variables.GetBool(key);}catch{return false;}
    }
    internal void drawWarnDetail(string key)
    {
        var w=Warnings.Find(key);
        if(w==null)return;
        int cur=0;
        try{cur=GameState.IsGameActive?(GameState.CurrentTurnNum??0):0;}catch{cur=0;}
        if(w.danger.Length>0)
        {
            bool trip=dangerTripped(key);
            var old=GUI.color;
            if(trip)GUI.color=new Color(1f,0.3f,0.3f);
            GUILayout.Label((trip?"TRIPPED: ":"Caution: ")+w.danger);
            GUI.color=old;
        }
        var gates=new System.Collections.Generic.List<Gate>(w.gates);
        gates.Sort((a,b)=>{
            int ra=a.turn>=cur?0:1;
            int rb=b.turn>=cur?0:1;
            if(ra!=rb)return ra-rb;
            return a.turn-b.turn;
        });
        foreach(var g in gates)
        {
            string when=g.turn>0?("T"+g.turn):"any";
            GUILayout.Label(when+" "+g.op+" "+g.val+" ("+g.conv+")");
        }
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
