import polars as pl
motogp=pl.read_csv("Motogp_2024_stats.csv",null_values=["","NA"])
print(motogp
      .select("RIDER","NAT","BIKE","WINS") #seleziona le colonne con solo questi titoli
      .filter(pl.col("WINS")>0)) #filtra in base ad un criterio, in questo caso che le vittorie siano maggiori di 0

# SELECT (WINS/RACES * 100) AS WIN_RATIO FROM motogp              comando sql

win_ratio=pl.col("WINS")/pl.col("RACES")*100 #percentuale di vittorie
print(motogp.select("RIDER",win_ratio.alias("wins ratio"))) #se non metto .alias la colonna di win_ratio si chiamerà WINS
                                                            #come nella formula di win_ratio.

print(motogp.with_columns(win_ratio.alias("wins ratio"))) #con .with_columns stampa tutta la tabella con l'aggiunta del
                                                          #nuovo dato in una nuova colonna.
print(motogp
      .with_columns(win_ratio.alias("wins ratio"))
      .filter(pl.col("wins ratio")>0)
      .sort("WINS","PODIUMS", descending=True))    #.sort ordina di default in ordine crescente o decrescente
                                                   # a seconda di descending (True=ordine decrescente)
                                                   # per le colonne passate in argomento ("Colonna1", "Colonna 2")

dnf_mean=pl.col("DNF").mean() #.mean() funzione che calcola la media di dati numerici di una colonna
print(motogp
      .group_by("NAT","BIKE")
      .agg(
          pl.col("DNF","WINS").mean() #calcola la media di vittorie e dnf per ogni nazionalità per ogni moto
      ))

print(motogp
      .with_columns(                     #con il seguente schema viene creata una colonna in base ale vittorie di ogni
          pl.when(pl.col("WINS")>0)      #pilota.
          .then(pl.lit("WINNER"))
          .otherwise(pl.lit("WINLESS"))
          .alias("WINNING STATUS")
      ))

print(motogp
      .group_by("NAT", "BIKE")
      .agg(
          frac_wins=pl.when(pl.col("WINS")>0)
          .then(pl.lit(1))
          .otherwise(pl.lit(0))
          .mean()
      )
      .sort("NAT","BIKE")) #ad esempio il 33.3% dei piloti spagnoli con Aprilia hanno vinto almeno una gara (1/3)
                           #esempio 2: il 66,7%> degli spagnoli con ducati hanno vinto almeno una gara (2/3)

#print(
#      flights.join(planes, on="tailnum", how="anti") #how indica il tipo di join che viene usato (inner, full, anti, ecc.)
#      .describe()
#)