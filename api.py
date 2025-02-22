import os
from vizro_ai import VizroAI
vizro_ai = VizroAI()
import vizro.plotly.express as px
from vizro import Vizro

df = px.data.gapminder(datetimes=True, pretty_names=True)
Vizro._reset()
user_question = """
Create a page showing 1 cards, 2 charts.
The first card says 'The Gapminder dataset is a detailed collection of global socioeconomic indicators over several decades. It includes data on GDP per capita, life expectancy, and population for numerous countries and regions. This dataset allows users to analyze development trends, health outcomes, economic growth, and demographic changes globally.'
The chart is a box plot showing life expectancy distribution. Put Life expectancy on the y axis, continent on the x axis, and color by continent.
The card takes 1 grid of the page space on the left and the box plot takes 3 grid space on the right.
The second chart is a pie chart showing average life expectancy for each country.
Add a filter to filter the box plot by year.
"""
dashboard = vizro_ai.dashboard([df], user_question)
Vizro().build(dashboard).run()
