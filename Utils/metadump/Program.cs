using System.Reflection.Metadata;
using System.Reflection.PortableExecutable;
if(args.Length<2){Console.WriteLine("usage: metadump <assembly> ns|types|members|strings [filter]");return 1;}
string path=args[0];
string mode=args[1];
string filter=args.Length>2?args[2]:"";
using var fs=File.OpenRead(path);
using var pe=new PEReader(fs);
var block=pe.GetMetadata();
unsafe
{
    byte* ptr=block.Pointer;
    var mr=new MetadataReader(ptr,block.Length);
    if(mode=="ns")
    {
        var counts=new Dictionary<string,int>();
        foreach(var h in mr.TypeDefinitions)
        {
            var td=mr.GetTypeDefinition(h);
            string ns=mr.GetString(td.Namespace);
            if(ns.Length==0)ns="<global>";
            counts[ns]=counts.TryGetValue(ns,out int c)?c+1:1;
        }
        foreach(var kv in counts.OrderByDescending(kv=>kv.Value).Take(80))
            Console.WriteLine($"{kv.Value}\t{kv.Key}");
    }
    else if(mode=="types")
    {
        var names=new List<string>();
        foreach(var h in mr.TypeDefinitions)
        {
            var td=mr.GetTypeDefinition(h);
            if(mr.GetString(td.Namespace)==filter)
            {
                int m=0,f=0,p=0,e=0;
                foreach(var _ in td.GetMethods())m++;
                foreach(var _ in td.GetFields())f++;
                foreach(var _ in td.GetProperties())p++;
                foreach(var _ in td.GetEvents())e++;
                names.Add($"{mr.GetString(td.Name)} (m={m} f={f} p={p} e={e})");
            }
        }
        names.Sort();
        foreach(var n in names)Console.WriteLine(n);
    }
    else if(mode=="members")
    {
        foreach(var h in mr.TypeDefinitions)
        {
            var td=mr.GetTypeDefinition(h);
            if(mr.GetString(td.Name)==filter)
            {
                Console.WriteLine($"TYPE: {mr.GetString(td.Namespace)}.{mr.GetString(td.Name)}");
                foreach(var mh in td.GetMethods())Console.WriteLine($"  M: {mr.GetString(mr.GetMethodDefinition(mh).Name)}");
                foreach(var fh in td.GetFields())Console.WriteLine($"  F: {mr.GetString(mr.GetFieldDefinition(fh).Name)}");
                foreach(var ph in td.GetProperties())Console.WriteLine($"  P: {mr.GetString(mr.GetPropertyDefinition(ph).Name)}");
                foreach(var eh in td.GetEvents())Console.WriteLine($"  E: {mr.GetString(mr.GetEventDefinition(eh).Name)}");
            }
        }
    }
    else if(mode=="strings")
    {
        byte[] meta;
        unsafe{byte* ptr2=block.Pointer;meta=new Span<byte>(ptr2,block.Length).ToArray();}
        int pos=16;
        int verLen=BitConverter.ToInt32(meta,pos-4);
        pos+=((verLen+3)&~3)+2;
        int nStreams=BitConverter.ToUInt16(meta,pos);
        pos+=2;
        int usOff=0,usSize=0;
        for(int i=0;i<nStreams;i++)
        {
            int o=BitConverter.ToInt32(meta,pos);
            int s=BitConverter.ToInt32(meta,pos+4);
            int e=pos+8;
            while(meta[e]!=0)e++;
            string nm=System.Text.Encoding.ASCII.GetString(meta,pos+8,e-pos-8);
            if(nm=="#US"){usOff=o;usSize=s;}
            pos=pos+8+(((e-pos-8+1+3)&~3));
        }
        var seen=new HashSet<string>();
        int off=usOff;
        int end=usOff+usSize;
        while(off<end)
        {
            byte b0=meta[off];
            int len,lb;
            if((b0&0x80)==0){len=b0;lb=1;}
            else if((b0&0xC0)==0x80){len=((b0&0x3F)<<8)|meta[off+1];lb=2;}
            else{len=((b0&0x1F)<<24)|(meta[off+1]<<16)|(meta[off+2]<<8)|meta[off+3];lb=4;}
            if(off+lb+len>end)break;
            string str=System.Text.Encoding.Unicode.GetString(meta,off+lb,len&~1);
            off+=lb+len;
            if(filter==""||str.Contains(filter)){if(seen.Add(str))Console.WriteLine(str);}
        }
    }
}
return 0;
