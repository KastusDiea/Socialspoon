import tkinter as tk
from tkinter import ttk, filedialog
from DataTransformService import DataTransformService
from CSVExportService import CSVExporter
from DataService import CreatorData, Platform, Video
from CreatorTableService import creators_to_dataframe
from DbPullService import DbPullService
from instagram_api import InstagramApiService


class CreatorIntelligence:
    def __init__(self, creator_db, api_service=None, transform=None, exporter=None, db_pull_service=None, instagram_api_service=None):
        self.creator_db = creator_db if creator_db is not None else []
        self.api = api_service
        self.transform = transform or DataTransformService()
        self.exporter = exporter
        self.db_pull_service = db_pull_service or DbPullService(
            api_service=self.api,
        )
        self.instagram_api = instagram_api_service or InstagramApiService(
            save_callback=self.db_pull_service.save_data,
            data_provider=lambda: self.creator_db,
        )
        self.db_pull_service.api_services["Instagram"] = self.instagram_api
        self.root = None
        self.table = None
        self.status = None
        try:
            self.root = tk.Tk()
            self.root.title("Creator Intelligence System")
            self.root.geometry("1200x700")
        except (tk.TclError, RuntimeError):
            self.root = None
            self.records = []
            return

        self.api_key = tk.StringVar(value=self.db_pull_service.api_key); self.keyword = tk.StringVar(); self.creator_name = tk.StringVar(); self.youtube = tk.BooleanVar(value=True); self.instagram = tk.BooleanVar(value=True); self.tiktok = tk.BooleanVar(value=True)
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
        creator_frame=tk.Frame(self.root); creator_frame.pack(fill="x",padx=10,pady=5)
        tk.Label(creator_frame,text="Creator:").pack(side="left")
        tk.Entry(creator_frame,textvariable=self.creator_name,width=30).pack(side="left",padx=5)
        self.creator_platform = tk.StringVar(value="YouTube")
        ttk.Combobox(creator_frame,textvariable=self.creator_platform,values=("YouTube", "Instagram"),state="readonly",width=12).pack(side="left",padx=5)
        tk.Button(creator_frame,text="Lade die letzten 10 Videos von dem Creator",command=self.load_creator_data).pack(side="left")
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
        tk.Button(b,text="Daten Aktualisieren",command=self.refresh_data).pack(side="right", padx=5)
        tk.Button(b,text="Export Current Table to CSV",command=self.export_csv).pack(side="right")


    def _to_dataframe(self):
        return creators_to_dataframe(self.creator_db)


    
    def display(self,records):
        if self.root is None or self.table is None or self.status is None:
            return
        for i in self.table.get_children(): self.table.delete(i)
        for r in records: self.table.insert('', 'end', values=[r.get(c,'') for c in self.columns])
        self.status.config(text=f"{len(records)} rows")



    def filter(self):
        if self.root is None:
            return
        dfobj=self._to_dataframe(); allowed=[]
        if self.youtube.get(): allowed.append('YouTube')
        if self.instagram.get(): allowed.append('Instagram')
        if self.tiktok.get(): allowed.append('TikTok')
        if allowed:
            df = self.transform.filter(dfobj, Platform=allowed)
        else:
            df = dfobj
        kw=self.keyword.get().strip()
        if kw: df = self.transform.filter(df, Creator=kw)
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
            try:
                self.db_pull_service.save_api_key(k)
                self.api.set_yt_api_key(k)
                self.status.config(text="YouTube API key set") if self.status else None
            except Exception:
                if self.status:
                    self.status.config(text="Failed to set API key")

    def load_creator_data(self):
        platform_name = self.creator_platform.get()
        selected_api = self.api if platform_name == "YouTube" else self.instagram_api
        if selected_api is None:
            if self.status:
                self.status.config(text="No API service configured")
            return

        creator_name = self.creator_name.get().strip()
        if not creator_name:
            if self.status:
                self.status.config(text="Please enter a creator name")
            return

        api_key_value = ""
        if platform_name == "YouTube":
            api_key = self.api_key.get().strip()
            if api_key:
                self.db_pull_service.save_api_key(api_key)
                self.api.set_yt_api_key(api_key)

            api_key_value = getattr(self.api, "youtubeAPIKey", None)
            if api_key_value is None:
                api_key_value = getattr(self.api, "key", None)

            if not api_key_value:
                if self.status:
                    self.status.config(text="YouTube API key is required")
                return

        try:
            platform = Platform(platform_name, api_key_value)
            creator = CreatorData(creator_name, platform)
            creator_data = selected_api.getRecentVideos(platform, creator)

            if not any(getattr(item, "name", None) == creator_name and getattr(item, "platform", None) and getattr(item.platform, "get_name", lambda: "")() == platform_name for item in self.creator_db):
                self.creator_db.append(creator_data)
            else:
                for idx, existing in enumerate(self.creator_db):
                    if getattr(existing, "name", None) == creator_name and getattr(existing, "platform", None) and getattr(existing.platform, "get_name", lambda: "")() == platform_name:
                        self.creator_db[idx] = creator_data
                        break

            self.db_pull_service.save_data(self.creator_db)
            self.records = self._to_dataframe().to_dict(orient='records')
            self.filter()
            if self.status:
                service_status = getattr(selected_api, "last_status", "")
                status = f"Loaded {creator_name} from {platform_name}"
                if service_status:
                    status = f"{status}: {service_status}"
                self.status.config(text=status)
        except Exception as exc:
            if self.status:
                self.status.config(text=f"Error: {exc}")

    def refresh_data(self):
        if self.api is None:
            if self.status:
                self.status.config(text="No API service configured")
            return

        try:
            refreshed = self.db_pull_service.refresh_data()
            self.creator_db[:] = refreshed
            self.filter()
            if self.status:
                self.status.config(text=f"Updated {len(refreshed)} creators")
        except Exception as exc:
            if self.status:
                self.status.config(text=f"Error refreshing data: {exc}")

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
        if self.root is None:
            return
        self.root.mainloop()
