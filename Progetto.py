import streamlit as st
import altair as alt
import polars as pl
import datetime as dt
import pandas as pd
data=pl.read_csv("https://raw.githubusercontent.com/nbugliar/motogp_regression/master/MotoGP_2005_2017.csv", null_values=[" ","NA","crash"])
st.write("Nella colonna Position, dove manca il valore, è perché il pilota non ha terminato il Gran Premio.")
st.write("PURTROPPO, PER RAGIONI A NOI IGNOTE, NEL DATASET MANCANO I RISULTATI DEL GP DI SPAGNA CLASSE 125cc. LE CLASSIFICHE DI QUELLA STAGIONE RISULTAERANNO QUINDI ALTERATE.")
st.title("Database Motomondiale 2005-2017")
st.header("Database completo da analizzare")
st.write(data)
#date=st.date_input("Inserire giorno:", dt.datetime(2020,1,5))
#st.write(data.filter(pl.col("Date")==date))
#st.write(data.select(pl.col("Date").cast(pl.Date)))
st.header("Classifiche generali")
col1, col2=st.columns(2)
year=col1.select_slider("Inserire anno:", range(2005,2018), key=1)
if year>2011:
    cat=col2.select_slider("Inserire Categoria:", ["MotoGP","Moto2","Moto3"])
elif (year>2009 and year<=2011):
    cat=col2.select_slider("Inserire Categoria:", ["MotoGP","Moto2","125cc"])
else:
    cat=col2.select_slider("Inserire Categoria:", ["MotoGP","250cc","125cc"])
# NEL GROUP BY TUTTE LE ALTRE COLONNE VANNO PERSE, PER CUI LE COLONNE DI FILTRAGGIO VANNO INSERITE.
col1.subheader("Classifica piloti")
col1.write(data.group_by("Year","Category","Rider_Name","Nationality").agg(pl.col("Points").sum(), pl.col("Bike").implode().list.unique())
         .filter(pl.col("Year")==year).filter(pl.col("Category")==cat).sort("Points", descending=True))
costr=data.group_by("Year", "TRK", "Category", "Bike").agg(pl.col("Points").max().alias("Tot_points")).sort("Year","Category","Bike", descending=True)
class_costr=costr.group_by("Year", "Category", "Bike").agg(pl.col("Tot_points").sum()).filter(pl.col("Year")==year, pl.col("Category")==cat).sort("Tot_points", descending=True)
col2.subheader("Classifica costruttori")
col2.write(class_costr)
#d_prog=data.filter(pl.col("Year")==year, pl.col("Category")==cat).group_by("Year","Category","Rider_Name","Date").agg(pl.col("Points").sum())
#st.write(d_prog)
#chart=alt.Chart(d_prog).mark_line().encode(alt.X("Date"), alt.Y("Points"), alt.Color("Rider_Name"))
#st.write(chart)
########
st.header("Risultati di ogni GP per categoria")
year1=st.select_slider("Inserire anno:", range(2005,2018), key=2)
dataytd=data.select("Year","TRK","Date")
dataytd_filt=dataytd.filter(pl.col("Year")==year1).select("TRK", "Date")
pd_ytd=pd.DataFrame(dataytd_filt)
pd_ytd=pd_ytd.rename(columns={0:"TRK",1:"Date"})
datasort1=pd_ytd.drop_duplicates(subset="TRK").sort_values("Date")
trk=st.multiselect("Inserire GP:", datasort1["TRK"].to_list())
if str("USA") not in trk:
    for i in trk:
        col11, col12, col13=st.columns(3)
        d1=data.filter(pl.col("TRK")==str(i)).filter(pl.col("Category")=="MotoGP").filter(pl.col("Year")==year1).select(
        "Category", "Position", "Rider_Name", "Nationality", "Team_Name", "Bike","Time","Year", "TRK", "Track")
        col11.write(d1)
        d2=data.filter(pl.col("TRK")==str(i)).filter(pl.col("Category").is_in(["250cc", "Moto2"])).filter(pl.col("Year")==year1).select(
        "Category", "Position", "Rider_Name", "Nationality", "Team_Name", "Bike","Time","Year", "TRK", "Track")
        col12.write(d2)
        d3=data.filter(pl.col("TRK")==str(i)).filter(pl.col("Category").is_in(["125cc", "Moto3"])).filter(pl.col("Year")==year1).select(
        "Category", "Position", "Rider_Name", "Nationality", "Team_Name", "Bike","Time","Year", "TRK", "Track")
        col13.write(d3)
else:
    d4=data.filter(pl.col("TRK").is_in(trk)).filter(pl.col("Category")=="MotoGP").filter(pl.col("Year")==year1).select(
        "Category", "Position", "Rider_Name", "Nationality", "Team_Name", "Bike","Time","Year", "TRK", "Track")
    st.write(d4)
########
st.header("Analisi pilota per pilota")
data_rider_points=data.group_by("Rider_Name","Year","Category","Bike").agg(pl.col("Points").sum())
st.write(data_rider_points)
#col1,col2,col3=st.columns(3)
#track=col2.multiselect("Inserire Paese:", ["QAT","ARG","AME","SPA","ARA"])
#cat=col3.multiselect("Inserire Categoria:", ["MotoGP","Moto2","Moto3","250cc","125cc"])
#col11,col21,col31,col41=st.columns(4)
#ses=col11.multiselect("Inserire sessione (RAC: gara, RAC2: ripartenza):", ["RAC","RAC2"])
#tcon=col21.multiselect("Inserire condizioni pista:", ["Dry", "Wet"])
#ttemp=col31.select_slider("Inserire temperatura asfalto:", range(20,60))
#atemp=col41.select_slider("Inserire temperatura aria:", range(15,40))
#points=st.select_slider("Inserire punteggio:", [0,1,2,3,4,5,6,7,8,9,10,11,13,16,20,25])
#st.write(data.filter(pl.col("Year")==year,pl.col("TRK").is_in(track), pl.col("Category").is_in(cat),
#                     pl.col("Session").is_in(ses),pl.col("Track_Condition").is_in(tcon),pl.col("Track_Temp")==ttemp,
#                     pl.col("Air_Temp")==atemp,pl.col("Points")==points))