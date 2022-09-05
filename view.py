import datetime
import tkinter as tk
from datetime import datetime as dt

from tkinter import Tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry

from database import DatabaseManager
from scraper import AcriticaScraper, G1Scraper, PortalAmazoniaScraper


class NewsScraperGUI(Tk):

    def __init__(self, title, width, height):
        super().__init__()
        self.title(title)
        self.window_width = width
        self.window_height = height
        self.geometry(f'{width}x{height}')
        self.resizable(False, False)
        self.configure(bg=NewsScraperDefaultTheme.COLOR_DARK_GREY)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.style = ttk.Style(self)
        NewsScraperDefaultTheme.configure_style(self.style)

        # frame keywords
        self.frame_keywords = ttk.Frame(self, width=self.window_width-30, height=height * 0.75, relief=tk.FLAT, style=NewsScraperDefaultTheme.TFRAME_STYLE_NAME)
        self.frame_keywords.place(x=15, y=15)

        # search keywords
        self.label_keywords = ttk.Label(self.frame_keywords, text='TERMOS', style=NewsScraperDefaultTheme.TLABEL_STYLE_NAME)
        self.label_keywords.place(x=25, y=25)
        self.svar_keywords = tk.StringVar()
        self.entry_keywords = ttk.Entry(self.frame_keywords, style=NewsScraperDefaultTheme.TENTRY_STYLE_NAME, textvariable=self.svar_keywords, width=120)
        self.entry_keywords.place(
            x=25,
            y=65
        )
        self.entry_keywords.update()

        # scraper selection
        self.use_scraper = (tk.BooleanVar(), tk.BooleanVar(), tk.BooleanVar())
        self.label_scrapers = ttk.Label(self.frame_keywords, text='PORTAIS', style=NewsScraperDefaultTheme.TLABEL_STYLE_NAME)
        self.label_scrapers.place(x=500, y=105)
        self.check1 = ttk.Checkbutton(
            self.frame_keywords,
            text='A Crítica',
            style=NewsScraperDefaultTheme.TCHECKBTN_STYLE_NAME,
            variable=self.use_scraper[0],
            onvalue=True,
            offvalue=False
        )
        self.check1.place(x=510, y=140)
        self.check2 = ttk.Checkbutton(
            self.frame_keywords,
            text='Portal Amazônia',
            style=NewsScraperDefaultTheme.TCHECKBTN_STYLE_NAME,
            variable=self.use_scraper[1],
            onvalue=True,
            offvalue=False
        )
        self.check2.place(x=510, y=180)
        self.check3 = ttk.Checkbutton(
            self.frame_keywords,
            text='G1 Notícias',
            style=NewsScraperDefaultTheme.TCHECKBTN_STYLE_NAME,
            variable=self.use_scraper[2],
            onvalue=True,
            offvalue=False
        )
        self.check3.place(x=510, y=220)

        # save options
        self.save_options = (tk.IntVar(), tk.IntVar(), tk.IntVar())
        self.label_save = ttk.Label(self.frame_keywords, text='SALVAR', style=NewsScraperDefaultTheme.TLABEL_STYLE_NAME)
        self.label_save.place(x=740, y=105)
        self.check_html = ttk.Checkbutton(
            self.frame_keywords,
            text='HTML',
            style=NewsScraperDefaultTheme.TCHECKBTN_STYLE_NAME,
            variable=self.save_options[0],
            onvalue=True,
            offvalue=False
        )
        self.check_html.place(x=750, y=140)
        self.check_txt = ttk.Checkbutton(
            self.frame_keywords,
            text='TXT',
            style=NewsScraperDefaultTheme.TCHECKBTN_STYLE_NAME,
            variable=self.save_options[1],
            onvalue=True,
            offvalue=False
        )
        self.check_txt.place(x=750, y=180)
        self.check_database = ttk.Checkbutton(
            self.frame_keywords,
            text='BANCO DE DADOS',
            style=NewsScraperDefaultTheme.TCHECKBTN_STYLE_NAME,
            variable=self.save_options[2],
            onvalue=True,
            offvalue=False
        )
        self.check_database.place(x=750, y=220)

        # date period
        self.label_from = ttk.Label(
            self.frame_keywords,
            text='DATA INICIAL',
            style=NewsScraperDefaultTheme.TLABEL_STYLE_NAME
        )
        self.label_from.place(x=25, y=105)

        self.date_period = (tk.StringVar(), tk.StringVar())
        agora = datetime.datetime.now()
        self.dt_entry_from = DateEntry(
            self.frame_keywords,
            selectmode='day',
            textvariable=self.date_period[0],
            year=agora.year,
            month=agora.month,
            day=agora.day,
            font=('Showcard Gothic', 16)
        )
        self.dt_entry_from.place(x=25, y=145)

        self.label_to = ttk.Label(
            self.frame_keywords,
            text='DATA FINAL',
            style=NewsScraperDefaultTheme.TLABEL_STYLE_NAME
        )
        self.label_to.place(x=255, y=105)

        self.dt_entry_to = DateEntry(
            self.frame_keywords,
            selectmode='day',
            textvariable=self.date_period[1],
            year=agora.year,
            month=agora.month,
            day=agora.day,
            font=('Showcard Gothic', 16)
        )
        self.dt_entry_to.place(x=255, y=145)

        # action buttons - test database connection
        self.btn_conn = ttk.Button(
            master=self,
            text='TESTAR CONEXÃO',
            style=NewsScraperDefaultTheme.TBUTTON_STYLE_NAME,
            command=NewsScraperGUI.verify_db_connection
        )
        self.btn_conn.place(x=self.window_width-460, y=self.window_height-60)

        # action buttons - start scraper
        self.btn_iniciar = ttk.Button(
            master=self,
            text='INICIAR',
            style=NewsScraperDefaultTheme.TBUTTON_STYLE_NAME,
            command=self.start_scraping
        )
        self.btn_iniciar.place(x=self.window_width-210, y=self.window_height-60)

        self.update_idletasks()

    @staticmethod
    def verify_db_connection():
        try:
            result = DatabaseManager.check_connection(DatabaseManager.POSTGRESQL_DB)
            if result:
                messagebox.showinfo(title='SUCESSO!', message='CONEXÃO COM O BANCO DE DADOS ESTABELECIDA!')
                if messagebox.askyesno(title='BANCO DE DADOS', message='DESEJA CRIAR O BANCO DE DADOS?'):
                    DatabaseManager.create_database(DatabaseManager.POSTGRESQL_DB)
                    messagebox.showinfo(title='BANCO DE DADOS', message='BANCO DE DADOS CRIADO COM SUCESSO!')
            else:
                messagebox.showwarning(title='AVISO!', message='NÃO FOI POSSÍVEL RECUPERAR A VERSÃO DO BANCOD E DADOS')
        except Exception as err:
            messagebox.showerror(title='ERRO!', message=f'NÃO FOI POSSÍVEL CONECTAR COM O BANCO DE DADOS: {str(err)}')

    def start_scraping(self):
        search_terms = [x.strip() for x in self.svar_keywords.get().split(',')]
        from_timestamp = dt.strptime(f"{self.dt_entry_from.get()} 00:00:00", '%d/%m/%Y %H:%M:%S').timestamp()
        to_timestamp = dt.strptime(f"{self.dt_entry_to.get()} 23:59:59", '%d/%m/%Y %H:%M:%S').timestamp()

        save_opt = [bool(x.get()) for x in self.save_options]
        scrapers = [
            AcriticaScraper(3, from_timestamp, to_timestamp, save_opt[0], save_opt[1], save_opt[2]),
            PortalAmazoniaScraper(3, from_timestamp, to_timestamp, save_opt[0], save_opt[1], save_opt[2]),
            G1Scraper(5, from_timestamp, to_timestamp, save_opt[0], save_opt[1], save_opt[2])
        ]
        for scraper, use in zip(scrapers, [x.get() for x in self.use_scraper]):
            if use:
                scraper.start(search_terms)

    def on_closing(self):
        if messagebox.askokcancel("SAIR", "Deseja realmente finalizar a aplicação?"):
            DatabaseManager.close_connection()
            self.destroy()


class NewsScraperDefaultTheme:

    COLOR_WHITE = '#f7f7f7'
    COLOR_WHITE2 = '#e7e8e7'
    COLOR_LIGHT_GREEN = '#20aa6d'
    COLOR_DARK_GREEN = '#147e4f'
    COLOR_LIGHT_GREY = '#414749'
    COLOR_DARK_GREY = '#2c3031'

    DEFAULT_THEME_NAME = 'clam'
    TFRAME_STYLE_NAME = 'news.search.TFrame'
    TLABEL_STYLE_NAME = 'news.search.TLabel'
    TENTRY_STYLE_NAME = 'news.search.TEntry'
    TCHECKBTN_STYLE_NAME = 'news.search.TCheckbutton'
    TBUTTON_STYLE_NAME = 'news.search.TButton'

    @staticmethod
    def configure_style(root):
        theme = ttk.Style(root)
        theme.theme_use(NewsScraperDefaultTheme.DEFAULT_THEME_NAME)
        theme.configure(
            NewsScraperDefaultTheme.TFRAME_STYLE_NAME,
            background=NewsScraperDefaultTheme.COLOR_LIGHT_GREY
        )
        theme.configure(
            NewsScraperDefaultTheme.TLABEL_STYLE_NAME,
            background=NewsScraperDefaultTheme.COLOR_LIGHT_GREY,
            foreground=NewsScraperDefaultTheme.COLOR_WHITE,
            font=('Showcard Gothic', 16)
        )
        theme.configure(
            NewsScraperDefaultTheme.TENTRY_STYLE_NAME,
            background=NewsScraperDefaultTheme.COLOR_LIGHT_GREY,
            foreground=NewsScraperDefaultTheme.COLOR_DARK_GREY,
            justify=tk.CENTER,
            font=('Showcard Gothic', 16)
        )
        theme.configure(
            NewsScraperDefaultTheme.TCHECKBTN_STYLE_NAME,
            background=NewsScraperDefaultTheme.COLOR_LIGHT_GREY,
            foreground=NewsScraperDefaultTheme.COLOR_WHITE, font=('Showcard Gothic', 16)
        )
        theme.map(NewsScraperDefaultTheme.TCHECKBTN_STYLE_NAME, background=[('active', NewsScraperDefaultTheme.COLOR_LIGHT_GREY)])

        theme.configure(
            NewsScraperDefaultTheme.TBUTTON_STYLE_NAME,
            background=NewsScraperDefaultTheme.COLOR_LIGHT_GREEN,
            foreground=NewsScraperDefaultTheme.COLOR_WHITE,
            font=('Showcard Gothic', 16)
        )
        theme.map(NewsScraperDefaultTheme.TBUTTON_STYLE_NAME,
                  background=[('active', NewsScraperDefaultTheme.COLOR_DARK_GREEN)])

        return theme


