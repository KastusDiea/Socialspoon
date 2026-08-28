import tkinter as tk
from tkinter import ttk, filedialog
import pandas as pd
from DataTransformService import DataTransformService
from CSVExportService import CSVExporter
from DataService import CreatorData, Video
class CreatorIntelligence:
    def __init__(self, creator_db, api_service=None, transform=None, exporter=None):
        self.creator_db = creator_db or []
        self.api = api_service
        self.transform = transform or DataTransformService()
        self.exporter = exporter
        self.root = tk.Tk(); self.root.title("Creator Intelligence System"); self.root.geometry("1200x700")
        self.api_key = tk.StringVar(); self.keyword = tk.StringVar(); self.youtube = tk.BooleanVar(value=True); self.instagram = tk.BooleanVar(value=True); self.tiktok = tk.BooleanVar(value=True)
        self.sort_column = None; self.sort_reverse = False
        self.columns = ["Platform","Creator","Subscribers","Title","Views","Likes","Upload Date"]
        self.build_ui()
        self.filter()

    def build_ui(self):
        top=tk.Frame(self.root); top.pack(fill="x",padx=10,pady=10)
        tk.Label(top,text="Creator Intelligence System",font=("Arial",18,"bold")).pack(side="left")
        api_frame=tk.Frame(top); api_frame.pack(side="right")
        tk.Label(api_frame,text="YouTube API Key:").pack(side="left")
        tk.Entry(api_frame,textvariable=self.api_key,width=30,show="*").pack(side="left",padx=5)
        tk.Button(api_frame,text="Set Key",command=self.set_api_key).pack(side="left")
        f=tk.Frame(self.root); f.pack(fill="x",padx=10,pady=5)
        tk.Checkbutton(f,text="YouTube",variable=self.youtube,command=self.filter).pack(side="left")
        tk.Checkbutton(f,text="Instagram",variable=self.instagram,command=self.filter).pack(side="left")
        tk.Checkbutton(f,text="Tiktok",variable=self.tiktok,command=self.filter).pack(side="left")
        tk.Label(f,text="Keyword:").pack(side="left",padx=(20,5))
        tk.Entry(f,textvariable=self.keyword,width=25).pack(side="left"); tk.Button(f,text="Filter",command=self.filter).pack(side="left",padx=5)
        tf=tk.Frame(self.root); tf.pack(fill="both",expand=True,padx=10,pady=10)
        self.table=ttk.Treeview(tf,columns=self.columns,show="headings")
        for c in self.columns: self.table.heading(c,text=c,command=lambda col=c: self.sort(col)); self.table.column(c,width=150)
        self.table.pack(side="left",fill="both",expand=True)
        sb=ttk.Scrollbar(tf,orient="vertical",command=self.table.yview); sb.pack(side="right",fill="y"); self.table.configure(yscrollcommand=sb.set)
        b=tk.Frame(self.root); b.pack(fill="x",padx=10,pady=10); self.status=tk.Label(b,text=""); self.status.pack(side="left")
        tk.Button(b,text="Export Current Table to CSV",command=self.export_csv).pack(side="right")


    def _to_dataframe(self):
        rows=[]
        for c in self.creator_db:
            p=getattr(c,'platform',None)
            pname = p.get_name() if p and hasattr(p,'get_name') else str(p or '')
            vids = getattr(c,'videos',[]) or []
            if not vids:
                rows.append({'Platform':pname,'Creator':getattr(c,'name',''),'Subscribers':getattr(c,'subscribers',''),'Title':'','Views':None,'Likes':None,'Upload Date':''})
            else:
                for v in vids:
                    rows.append({'Platform':pname,'Creator':getattr(c,'name',''),'Subscribers':getattr(c,'subscribers',''),'Title':getattr(v,'title',''),'Views':getattr(v,'views',None),'Likes':getattr(v,'likes',None),'Upload Date':getattr(v,'upload_date','')})
        return pd.DataFrame(rows)


    
    def display(self,records):
        for i in self.table.get_children(): self.table.delete(i)
        for r in records: self.table.insert('', 'end', values=[r.get(c,'') for c in self.columns])
        self.status.config(text=f"{len(records)} rows")



    def filter(self):
        dfobj=self._to_dataframe(); allowed=[]
        if self.youtube.get(): allowed.append('YouTube')
        if self.instagram.get(): allowed.append('Instagram')
        if self.tiktok.get(): allowed.append('TikTok')
        df = self.transform.filter(dfobj, Platform=allowed[0]) if len(allowed)==1 else dfobj
        kw=self.keyword.get().strip()
        if kw: df = self.transform.filter(df, Creator=kw)  # TODO: DataTransformService should support contains
        records = df.to_dict(orient='records')
        self.records=records; self.display(records)



    def sort(self, column):
        dfobj=self._to_dataframe(); asc = not self.sort_reverse
        df = self.transform.sort(dfobj, by=column, ascending=asc)
        self.sort_reverse = not self.sort_reverse
        self.records = df.to_dict(orient='records'); self.display(self.records)



    def set_api_key(self):
        k=self.api_key.get().strip();
        if self.api: 
            try: self.api.set_yt_api_key(k)
            except: pass


    def export_csv(self):
        if not getattr(self,'records',None): return
        filename = filedialog.asksaveasfilename(defaultextension='.csv',filetypes=[('CSV files','*.csv')])
        if not filename: return
        creators_map={}
        for r in self.records:
            key=(r.get('Creator',''),r.get('Platform',''))
            if key not in creators_map:
                # reuse original creator object if present
                orig = next((c for c in self.creator_db if getattr(c,'name','')==key[0] and (getattr(c,'platform').get_name() if getattr(c,'platform',None) else '')==key[1]), None)
                if orig: creators_map[key]=CreatorData(orig.name, orig.platform, orig.subscribers, [])
                else: creators_map[key]=CreatorData(key[0], None, r.get('Subscribers',0), [])
            if r.get('Title'):
                v=Video(r.get('Title'), r.get('Views') or 0, r.get('Likes') or 0, r.get('Upload Date') or '')
                creators_map[key].videos.append(v)
        creator_list=list(creators_map.values())
        try:
            if self.exporter: setattr(self.exporter,'filename',filename); self.exporter.save_creator_database(creator_list)
            else: CSVExporter(filename=filename).save_creator_database(creator_list)
        except Exception:
            # fallback simple csv
            import csv as _csv
            cols=self.columns
            with open(filename,'w',newline='',encoding='utf-8') as f:
                w=_csv.DictWriter(f,fieldnames=cols); w.writeheader(); w.writerows(self.records)


    def run(self): 
        self.root.mainloop()
