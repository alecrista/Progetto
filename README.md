# DATABASE MOTOMONDIALE 2005-2017
Con questo progetto andremo ad analizzare il meglio (e il peggio) del Motomondiale nel periodo 2005-2017. Il database originale lo si può trovare sulla seguente piattaforma:  
[**Database originale**](https://raw.githubusercontent.com/nbugliar/motogp_regression/master/MotoGP_2005_2017.csv)  
Le operazioni eseguite, messe insieme, non saranno altro che un'analisi esplorativa, un pochino particolare forse, sui dati di cui dispone il database.  
Trattandosi di competizioni le principali misure che verranno prese saranno punteggie e velocità, ma ci saranno anche altri dati curiosi da analizzare.  
### Piccoli problemi inziali
Il database originale non è perfetto: ho dovuto inizialmente rimuovere i dati inutili, come ad esempio, in caso di gare interrotte dalla bandiera rossa con successiva ripartenza, le classifiche delle gare al momento dell'interruzione. Ai fini della nostra analisi esse sarebbero state inutili, pocihé la classifica finale, in quei casi appunto di ripartenza, è data dall'arrivo della _"seconda"_ gara.  
Poi ho dovuto aggiungere punteggi mancanti a certi Gran Premi (ad esempio il GP di Repubblica Ceca 2005 classe MotoGP), per motivi ignoti e poi sostituire eventuali doppioni sia tra le case costruttrici che tra i piloti (es. nel database il pilota Dani PEDROSA appariva sia con il nome "Dani PEDROSA " che con il nome "Daniel PEDROSA", quindi il programma lo avrebbe considerato come 2 piloti diversi). Per farlo ho usato il comando:  
'''
data=data.with_columns(
    pl.col("Rider_Name").str.replace("Daniel PEDROSA","Dani PEDROSA").alias("Rider_Name"),
    pl.col("Bike").str.replace("Yamaha Forward","Forward Yamaha").alias("Bike")
)
'''
## Introduzione
Per iniziare era necessario che un utente, passandomi il termine, "ignorante" in questo campo ottenesse giusto un'infarinatura su chi, a livello di successo puro, tra costruttori e piloti, fosse effettivamente stato il migliore, cosicchè ci si trovasse molto meno spaesati di fronte a moli così elevate di dati di cui magari non si conosce niente.
## Classifiche generali
In questa prima sezione l'utente si sar