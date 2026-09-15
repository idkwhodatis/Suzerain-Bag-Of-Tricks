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
    internal static bool noTextField=false;
    internal static GUIContent tipped(string text,string tip)
    {
        try{return new GUIContent(text,tip);}
        catch{return new GUIContent(text);}
    }
    internal System.Collections.Generic.Dictionary<string,string> tipCache=new System.Collections.Generic.Dictionary<string,string>();
    internal string hoverKey="";
    internal double hoverStart=0;
    internal bool hoverSeen=false;
    internal string tipFor(string key,string group)
    {
        string ck=key.Length>0?("k:"+key):("g:"+group);
        string t;
        if(tipCache.TryGetValue(ck,out t))return t;
        System.Collections.Generic.List<string> ks=new System.Collections.Generic.List<string>();
        if(key.Length>0)
        {
            ks.Add(key);
            foreach(var m in matesOf(key))if(m!=key&&ks.Contains(m)==false)ks.Add(m);
        }
        else
        {
            var g=FindGroup(group);
            if(g!=null)
            {
                foreach(var k in g.members)if(ks.Contains(k)==false)ks.Add(k);
                foreach(var arr in g.optKeys)foreach(var k in arr)if(ks.Contains(k)==false)ks.Add(k);
            }
        }
        t=Strings.T("menu.modifies");
        foreach(var k in ks)t+="\n- "+k;
        tipCache[ck]=t;
        return t;
    }
    internal static string[] matesOf(string key)
    {
        foreach(var e in MenuData.Mates)
        {
            int i=e.IndexOf('=');
            if(i>0&&e.Substring(0,i)==key)return e.Substring(i+1).Split('|');
        }
        return new string[]{key};
    }
    internal void draw()
    {
        GUI.Box(win,"");
        Rect bar=new Rect(win.x,win.y,win.width,20);
        GUI.Box(bar,"BagOfTricks ("+Strings.T("app.hotkey")+")");
        dragBar(bar);
        GUILayout.BeginArea(new Rect(win.x+4,win.y+24,win.width-8,win.height-28));
        hoverSeen=false;
        try{drawBody();}
        catch(System.Exception ex)
        {
            if(drawError==""){drawError=ex.ToString();Melon<Core>.Logger.Error(drawError);}
            GUILayout.Label(drawError);
        }
        GUILayout.EndArea();
        try
        {
            if(hoverSeen==false)hoverKey="";
            if(hoverKey.Length>0&&UnityEngine.Time.realtimeSinceStartup-hoverStart>=1.0)
            {
                var m=Mouse.current;
                if(m!=null)
                {
                    Vector2 mp=m.position.ReadValue();
                    mp.y=Screen.height-mp.y;
                    int lines=1;
                    foreach(var ch in hoverKey)if(ch=='\n')lines++;
                    float bx=mp.x+16;
                    if(bx>Screen.width-450)bx=Screen.width-450;
                    GUI.Box(new Rect(bx,mp.y-10,440,20+16*lines),hoverKey);
                }
            }
        }
        catch{}
    }
    internal void drawKeyLabel(string text,string tip)
    {
        GUILayout.Label(text,GUILayout.Width(150));
        try
        {
            var m=Mouse.current;
            if(m==null)return;
            Rect r=GUILayoutUtility.GetLastRect();
            Vector2 mp=m.position.ReadValue();
            mp.y=Screen.height-mp.y;
            if(r.Contains(mp))
            {
                hoverSeen=true;
                if(hoverKey!=tip){hoverKey=tip;hoverStart=UnityEngine.Time.realtimeSinceStartup;}
            }
        }
        catch{}
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
    internal bool langOpen=false;
    internal string expandedKey="";
    internal string mode="sordland";
    internal System.Collections.Generic.Dictionary<string,string> intBuffers=new System.Collections.Generic.Dictionary<string,string>();
    internal System.Collections.Generic.Dictionary<string,bool> openGroups=new System.Collections.Generic.Dictionary<string,bool>();
    internal bool isOpen(string id)
    {
        bool o=false;
        if(openGroups.TryGetValue(id,out o))return o;
        return true;
    }
    internal static GroupDef FindGroup(string name)
    {
        foreach(var g in Groups.All)if(g.name==name)return g;
        foreach(var g in MenuData.Composites)if(g.name==name)return g;
        return null;
    }
    internal static string repKey(GroupDef g)
    {
        if(g==null)return "";
        if(g.members.Length>0)return g.members[0];
        foreach(var ks in g.optKeys)if(ks.Length>0)return ks[0];
        return "";
    }
    internal static bool isGroupedKey(string key)
    {
        foreach(var mg in MenuData.Groups)foreach(var r in mg.rows)
        {
            if(r.kind!="group"&&r.key==key)return true;
        }
        return false;
    }
    internal static bool packMatch(string key,string filter)
    {
        if(filter=="all")return true;
        if(key.StartsWith("SharedSupport."))return true;
        if(filter=="sordland")return key.StartsWith("BaseGame")||key.StartsWith("GameCondition");
        return key.StartsWith("Rizia");
    }
    internal void drawBody()
    {
        bool active=false;
        try{active=GameState.IsGameActive;}catch{active=false;}
        string head=Strings.T("menu.noCampaign");
        try{if(active)head=GameState.CurrentStoryPackName+" T"+GameState.CurrentTurnNum+" S"+GameState.CurrentStepNum;}catch{head=Strings.T("menu.noCampaign");}
        GUILayout.Label(head);
        if(active==false)GUILayout.Label(Strings.T("menu.loadHint"));
        if(Dump.lastResult.Length>0)GUILayout.Label(Dump.lastResult);
        GUILayout.BeginHorizontal();
        if(GUILayout.Button(mode=="sordland"?"["+Strings.T("menu.sordland")+"]":Strings.T("menu.sordland")))mode="sordland";
        if(GUILayout.Button(mode=="rizia"?"["+Strings.T("menu.rizia")+"]":Strings.T("menu.rizia")))mode="rizia";
        if(GUILayout.Button(mode=="settings"?"["+Strings.T("menu.settings")+"]":Strings.T("menu.settings")))mode="settings";
        GUILayout.EndHorizontal();
        GUILayout.BeginHorizontal();
        GUILayout.Label(Strings.T("menu.search"),GUILayout.Width(50));
        if(noTextField)GUILayout.Label(search);
        else
        {
            try{search=GUILayout.TextField(search);}
            catch(System.Exception ex)
            {
                noTextField=true;
                Melon<Core>.Logger.Warning("search field unavailable: "+ex.GetType().Name);
            }
        }
        GUILayout.EndHorizontal();
        if(mode=="settings")
        {
            GUILayout.Label("BagOfTricks "+Strings.T("menu.versionBy").Replace("{0}",Core.Version).Replace("{1}",Core.Author));
            GUILayout.BeginHorizontal();
            GUILayout.Label(Strings.T("menu.language"),GUILayout.Width(50));
            if(GUILayout.Button((Strings.current=="en"?"English":"简体中文")+(langOpen?" ▲":" ▼"),GUILayout.Width(120)))langOpen=!langOpen;
            GUILayout.EndHorizontal();
            if(langOpen)
            {
                if(GUILayout.Button("English")){setLang("en");langOpen=false;}
                if(GUILayout.Button("简体中文")){setLang("zh-Hans");langOpen=false;}
            }
            GUILayout.BeginHorizontal();
            GUILayout.Label(Strings.T("menu.experimental"),GUILayout.Width(50));
            if(GUILayout.Button(isExperimental()?Strings.T("menu.on"):Strings.T("menu.off"),GUILayout.Width(80)))setExperimental(!isExperimental());
            GUILayout.EndHorizontal();
            GUILayout.BeginHorizontal();
            if(GUILayout.Button(Strings.T("menu.dumpNow")))Dump.run();
            GUILayout.EndHorizontal();
            if(Dump.lastResult.Length>0)GUILayout.Label(Dump.lastResult);
            GUILayout.Label(Strings.T("menu.dumpNote"));
            GUILayout.Label(Strings.T("menu.numberHint"));
            return;
        }
        bool en=GUI.enabled;
        GUI.enabled=active;
        bool enMax=GUI.enabled;
        GUI.enabled=active;
        if(mode=="sordland"&&GUILayout.Button(Strings.T("menu.maxMoney")))maxSordland();
        if(mode=="rizia"&&GUILayout.Button(Strings.T("menu.maxResources")))maxRizia();
        GUI.enabled=enMax;
        GUI.enabled=en;
        scroll=GUILayout.BeginScrollView(scroll);
        drawPackGroups(mode);
        drawExtrasPack(mode,mode=="sordland"?Strings.T("menu.extrasSordland"):Strings.T("menu.extrasRizia"));
        GUILayout.EndScrollView();
    }
    internal void setLang(string name)
    {
        Strings.current=name;
        try
        {
            if(Core.Instance!=null&&Core.Instance.langEntry!=null)Core.Instance.langEntry.Value=name;
        }
        catch{}
    }
    internal static bool isExperimental()
    {
        try
        {
            if(Core.Instance!=null&&Core.Instance.experimentalEntry!=null)return Core.Instance.experimentalEntry.Value;
        }
        catch{}
        return false;
    }
    internal static void setExperimental(bool v)
    {
        try
        {
            if(Core.Instance!=null&&Core.Instance.experimentalEntry!=null)Core.Instance.experimentalEntry.Value=v;
        }
        catch{}
    }
    internal void drawPackGroups(string p)
    {
        bool active=false;
        try{active=GameState.IsGameActive;}catch{active=false;}
        string q=search.ToLowerInvariant();
        foreach(var mg in MenuData.Groups)
        {
            if(mg.pack!=p)continue;
            string id=p+"/"+mg.name;
            string gtitle=Strings.T("group."+mg.name);
            if(GUILayout.Button((isOpen(id)?"- ":"+ ")+gtitle))openGroups[id]=!isOpen(id);
            if(isOpen(id)==false)continue;
            bool en=GUI.enabled;
            GUI.enabled=active;
            foreach(var r in mg.rows)
            {
                if(search.Length>0&&r.label.ToLowerInvariant().Contains(q)==false
                    &&r.key.ToLowerInvariant().Contains(q)==false
                    &&r.group.ToLowerInvariant().Contains(q)==false)continue;
                GUILayout.BeginHorizontal();
                drawKeyLabel(Strings.T("field."+r.label),tipFor(r.key,r.group));
                try{drawMenuRow(r);}
                catch{GUILayout.Label(Strings.T("menu.err"),GUILayout.Width(80));}
                GUILayout.EndHorizontal();
            }
            GUI.enabled=en;
        }
    }
    internal void drawMenuRow(MenuRow r)
    {
        if(r.kind=="int")drawInt(r.key);
        else if(r.kind=="bool")drawBool(r.key);
        else if(r.kind=="group")
        {
            var g=FindGroup(r.group);
            if(g==null){GUILayout.Label("?",GUILayout.Width(80));return;}
            drawGroup(g);
            string rk=repKey(g);
            if(rk.Length>0)drawWarnToggle(rk);
        }
        else GUILayout.Label("?",GUILayout.Width(80));
    }
    internal void drawExtrasPack(string p,string title)
    {
        string id="extras/"+p;
        if(GUILayout.Button((isOpen(id)?"- ":"+ ")+title))openGroups[id]=!isOpen(id);
        if(isOpen(id)==false)return;
        if(isExperimental()==false){GUILayout.Label(Strings.T("menu.experimentalOff"));return;}
        bool active=false;
        try{active=GameState.IsGameActive;}catch{active=false;}
        bool en=GUI.enabled;
        GUI.enabled=active;
        string q=search.ToLowerInvariant();
        int shown=0;
        int skipped=0;
        foreach(var e in Keys.Typed)
        {
            if(isGroupedKey(e.name))continue;
            if(packMatch(e.name,p)==false)continue;
            string label=shortName(e.name);
            if(search.Length>0&&label.ToLowerInvariant().Contains(q)==false
                &&e.name.ToLowerInvariant().Contains(q)==false)continue;
            if(shown>=400){skipped++;continue;}
            shown++;
            GUILayout.BeginHorizontal();
            drawKeyLabel(label,tipFor(e.name,""));
            try
            {
                if(e.isBool)drawBool(e.name);
                else drawInt(e.name);
                drawWarnToggle(e.name);
            }
            catch{GUILayout.Label(Strings.T("menu.err"),GUILayout.Width(80));}
            GUILayout.EndHorizontal();
            if(expandedKey==e.name)drawWarnDetail(e.name);
        }
        if(skipped>0)GUILayout.Label(Strings.T("menu.more").Replace("{0}",skipped.ToString()));
        GUI.enabled=en;
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
        if(label=="ON")label=Strings.T("menu.on");
        else if(label=="OFF")label=Strings.T("menu.off");
        else label=Strings.T("menu.mix");
        if(GUILayout.Button(label,GUILayout.Width(80)))
        {
            bool target=all==false;
            foreach(var k in keys)Variables.Set(k,target);
        }
    }
    internal void drawInverse(string winKey,string loseKey)
    {
        bool win=Variables.GetBool(winKey);
        if(GUILayout.Button(win?Strings.T("menu.win"):Strings.T("menu.lost"),GUILayout.Width(80)))
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
        string label=cur>=0?g.optNames[cur]:Strings.T("menu.none");
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
        if(noTextField){drawIntFallback(key,v);return;}
        try
        {
            string buf;
            if(intBuffers.TryGetValue(key,out buf)==false){buf=v.ToString();intBuffers[key]=buf;}
            string focused="";
            try{focused=GUI.GetNameOfFocusedControl();}
            catch(System.Exception ex)
            {
                noTextField=true;
                Melon<Core>.Logger.Warning("focus api unavailable, stepper fallback: "+ex.GetType().Name);
                drawIntFallback(key,v);
                return;
            }
            string ctl="int_"+key;
            if(focused!=ctl){buf=v.ToString();intBuffers[key]=buf;}
            if(GUILayout.Button("-",GUILayout.Width(30))){Variables.Set(key,v-1);intBuffers[key]=(v-1).ToString();}
            GUI.SetNextControlName(ctl);
            string nv=buf;
            try{nv=GUILayout.TextField(buf,GUILayout.Width(60));}catch{nv=buf;}
            intBuffers[key]=nv;
            if(GUILayout.Button("+",GUILayout.Width(30))){Variables.Set(key,v+1);intBuffers[key]=(v+1).ToString();}
            bool commit=false;
            try{
                var ev=Event.current;
                if(ev!=null&&focused==ctl&&ev.type==EventType.KeyDown&&(ev.keyCode==KeyCode.Return||ev.keyCode==KeyCode.KeypadEnter))commit=true;
            }catch{commit=false;}
            if(commit)
            {
                int parsed=0;
                if(int.TryParse(nv,out parsed)&&parsed!=v)Variables.Set(key,parsed);
                intBuffers[key]=Variables.GetInt(key).ToString();
            }
        }
        catch(System.Exception ex)
        {
            noTextField=true;
            Melon<Core>.Logger.Warning("textfield path unavailable, stepper fallback: "+ex.GetType().Name);
            drawIntFallback(key,v);
        }
    }
    internal void drawIntFallback(string key,int v)
    {
        GUILayout.Label(v.ToString(),GUILayout.Width(50));
        if(GUILayout.Button("-",GUILayout.Width(30)))Variables.Set(key,v-1);
        if(GUILayout.Button("+",GUILayout.Width(30)))Variables.Set(key,v+1);
    }
    internal void drawBool(string key)
    {
        bool v=Variables.GetBool(key);
        if(GUILayout.Button(v?Strings.T("menu.on"):Strings.T("menu.off"),GUILayout.Width(80)))Variables.Set(key,!v);
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
            GUILayout.Label((trip?Strings.T("menu.tripped"):Strings.T("menu.caution"))+w.danger);
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
