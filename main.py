# -*- coding: utf-8 -*-
from logs import Logger
from view import NewsScraperGUI


if __name__ == '__main__':
    Logger.configure()
    gui = NewsScraperGUI('NEWS SCRAPER TOOL V1.0', 1040, 380)
    gui.mainloop()
