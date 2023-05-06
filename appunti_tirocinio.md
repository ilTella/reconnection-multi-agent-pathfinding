# Tirocinio

Il lavoro svolto verte allo studio del problema del MAPF: Multi-Agent Path Finding e allo sviluppo di algoritmi per risolvere delle sue varianti.

Il problema consiste nel pianificare i percorsi di movimento per agenti (ad esempio, robot in un magazzino automatizzato) che devono spostarsi da un punto di partenza ad uno di arrivo, detto anche di goal, senza scontrarsi con ostacoli o tra di loro.

Essendo un problema complesso, non esiste un'unica soluzione elementare per risolverlo, ma ci sono piuttosto diversi approcci: è possibile risolvere il problema in modo ottimo, sacrificando però le performance quando il numero di agenti coinvolti inizia a crescere, oppure puntare ad una soluzione sub-ottimale, ma che si possa ottenere in tempo ragionevole per un numero più elevato di agenti.

## Studio algoritmi MAPF

(da scrivere)

## Problema dell'agent meeting

Una variante interessante del MAPF problem è quella in cui gli agenti non devono semplicemente spostarsi da un punto A di partenza ad un punto B di goal, ma hanno invece un insieme comune di punti di goal, e l'importante è che ogni agente arrivi ad occupare uno di quei punti, senza badare a chi finisce dove.

Sebbene possa sembrare una versione più semplice del problema, la difficoltà aggiuntiva diventa evidente illustrando la seconda caratteristica di questa variante: i punti di goal che gli agenti devono andare a raggiungere non sono prestabiliti, ma vengono determinati facendo in modo che rispettino delle caratteristiche.
Una volta arrivati ai goal, gli agenti devono essere tutti connessi tra di loro, oppure si può decidere che un agente può avere al massimo n intermediari, tramite i quali è connesso alla totalità degli altri agenti.
Due agenti sono connessi se i vertici che occupano sono connessi su un grafo di connessione costruito a partire dal grafo primario, utilizzando una definizione di connessione.
Questo generalmente significa che gli agenti dovranno andare ad incontrarsi in punti vicini tra di loro e che non presentino ostacoli che si staglino tra loro.
Per decidere quale agente si deve dirigere ad un goal sip uò considerare l'agente che percorrerebbe il percorso minimo, oppure cercare di minimizzare il tragitto medio di tutti gli agenti.
In ogni caso si assume che ogni vertice del grafo primario sia connesso ad ogni altro vertice di tale grafo, così non si considerano grafi degeneri in cui ci siano zone non raggiungibili, in quanto tali grafi avrebbero difficilmente applicazione in contesti utili del mondo reale.
Tale assunzione ovviamente non vale per il grafo di connessione, dove vertici lontani tra loro, o tra i quali sono piazzati diversi ostacoli non permettono la comunicazione tra agenti.

Il requisito di connessione ha un corrispettivo in situazioni reali tali per cui gli agenti devono poter comunicare tra di loro, ad esempio in un magazzino automatizzato i robot potrebbero avere il compito di monitorarsi a vicenda, per controllare il loro funzionamento sia corretto.

### Algoritmo

Per prima cosa prendo in esame un'istanza di problema, cioè una mappa, definita dalle sue dimensioni (lunghezza e larghezza) e dalla posizione degli ostacoli, e le posizioni di partenza e di goal degli agenti.

A questo punto genero il grafo di connessione a partire dalla mappa, utilizzando una definizione di connessione.
L'assunzione più semplice è che tutti i vertici siano connessi, ma ciò è inutile; una definizione più interessante è basata sulla distanza: se due vertici hanno una distanza minore di un certo parametro, allora sono connessi.
Una definizione più complessa combina la distanza tra vertici e gli ostacoli posti tra loro: due vertici sono connessi se tra loro la distanza è minore di un certo parametro, che diminuisce se tra loro ci sono degli ostacoli.
Ciò cerca di simulare un segnale wireless che si indebolisce se deve passare attraverso superfici solide.

Successivamente utilizzo il grafo di connessione creato per trovare n goal (dove n è il numero di agenti) che rispettino le condizioni stabilite, quindi che siano o tutti connessi, oppure connessi tramite al massimo k intermediari.
Posso servirmi delle posizioni di partenza per cercare di trovare un gruppo di vertici vicino agli agenti.

Il passo successivo consiste nell'assegnare ogni goal ad un agente.
Posso farlo in modo arbitrario, oppure cercando di minimizzare il costo del percorso di ogni agente, oppure il costo medio per tutti gli agenti.

Infine, avendo una mappa, delle posizioni di partenza e di goal, posso passare l'istanza modificata del problema ad un risolutore che utilizzi l'algoritmo CBS, e ottenere così una soluzione al problema.
