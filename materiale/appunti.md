# MAPF (Multi-agent pathfinding)

## Introduzione

### Definizione problema

Ci sono un gruppo di agenti ed ognuno deve muoversi da una posizione di partenza ad una di goal.
Ogni agente, ad ogni step, può muoversi in una delle quattro direzioni cardinali oppure attendere nella cella corrente.

Non sono permesse collisioni, che solitamente sono definite nel seguente modo:

* **vertex collision**: due agenti cercano di muoversi nella stessa cella allo stesso tempo
* **edge collision**: due agenti adiacenti cercano di scambiarsi di posto

Si può cercare di minimizzare la somma dei costi, oppure il costo massimo tra quelli di tutti gli agenti.

### Aspetti critici del problema

Bisogna trovare algoritmi che lavorino bene con numeri molto elevati di agenti, infatti nelle situazioni reali (come i magazzini Amazon) possono esserci diverse centinaia di agenti di cui pianificare il movimento.
Servono perciò algoritmi con una buona scalabilità.

Serve considerare gli agenti nel loro insieme, infatti calcolando i percorsi per i singoli agenti potrebbero formarsi situazioni di deadlock oppure congestioni e inefficienze.
Questo porta ad un incremento della complessità computazionale e bisogna ragionare su possibili soluzioni.

Potrebbero esserci dei ritardi nel movimento degli agenti, se parliamo di agenti nel mondo fisico, e sarebbe una buona idea creare un sistema robusto a questi eventuali ritardi.
Una prima strategia consiste nel ritardare tutti i robot se si rileva un ritardo in uno di loro.
Una seconda idea prevede di di ripianificare in caso di plan failure. Il problema è che la fase di planning è lenta e infatti avviene prima che i robot si muovano.
Si potrebbero usare tecniche di reinforcement e machine learning per velocizzare il planning, ma si è visto che non hanno una buona resa.

La soluzione migliore è: trovare un plan per il MAPF (lento), in un loop, determinare la velocità a cui ogni agente dovrebbe muoversi all'interno del proprio cammino (veloce) e, solo se il problema diventa irrisolvibile, cercare un nuovo plan

MAPF-POST fa uso di un temporal network per post-processare, in tempo polinomiale, un MAPF plan che gli viene dato per permetterne una esecuzione robusta.
Si crea un grafo delle precedenze, dove si considerano eventi (l'agente A entra nella cella x) e precedenze; si impongono vincoli del tipo "l'agente B deve uscire dalla cella x prima che l'agente A ci entri".
Poi si utilizza la ricerca operativa per i tempi minimi di arrivo di ogni agente ad ogni cella per garantire il rispetto dei constraint stabiliti.

Nella simulazione si potrebbero non avere le risorse necessarie, allora si possono tracciare i movimenti di un gruppo di agenti reali, avere un gruppo di agenti simulati fedelmente (leggi fisiche considerate) e un ultimo gruppo simulato in maniera più lasca.

### Applicazioni

Il problema del MAPS si trova in diverse situazioni:

* gestione treni e aeroporti
* magazzini 
* videogiochi
* multi-arm assembly
* pipe routing
* autonomous intersections
* mail sorting

### Approcci

* Search based

* Procedure based

* Reduction solvers

## Algoritmi ottimali

### Search-based

### A*-based search in the joint space state

Si definisce uno stato come la posizione di ogni agente nello spazio e si esegue una ricerca con A* su questo insieme degli stati.

L'algoritmo è ottimale ma la complessità del calcolo cresce esponenzialmente, perciò è assolutamente impraticabile se non per un numero estremamente piccolo di agenti.

Si può migliorare la situazione con **independence detection**, dove si dividono gli agenti in gruppi indipendenti e e si risolve ogni gruppo in modo separato. In questo modo si riduce il numero di agenti.

Si può anche cercare di ridurre il branching factor, idea che sta alla base di M*. Lavora sullo spazio globale degli stati ma espande un'azione alla volta, se si verifica un conflitto tra due agenti, M* torna indietro e genera tutti i possibili figli.

Altre migliorie sono la **operator decomposition** e la **enhanced partial expansion**.

### non-A* algorithms

Nuovi algoritmi che usano approcci diversi

### Increasing cost tree search (ICTS)

Algoritmo a due livelli: l'high level chiede se è possibile trovare una soluzione con determinati costi e il low level cerca e da una risposta, a quel punto l'high level alza i costi e si continua.
In questo modo si esplora l'albero degli stati in modo incrementale.

Ci sono casi "patologici" dove l'algoritmo ci mette molto più del dovuto.

### Conflict-based search (CBS)

Si pianifica per gli agenti separatamente, se poi ci sono conflitti si sdoppia la ricerca: da un lato si inserisce un constraint per il primo agente, dall'altro per il secondo agente.
Un constraint è legato ad un agente, una cella e uno step di tempo.

Lo splitting può essere non-disjoint o disjoint: nel primo caso si impone un constraint negativo prima per l'agente A e poi per l'agente B; nel secondo caso il constraint è negativo per A ("non puoi trovarti in quella cella") e positivo per B ("DEVI trovarti in quella cella").
Il disjoint splitting può portare a dei risparmi in termini di tempo di calcolo.

Si posso individuare delle **collision symmetries**, diversi stati che nella pratica sono corrispondenti in quanto si tratta della stessa collisione.
A questo punto ad un passo di CBS si possono aggiungere più constraint, del tipo "l'agente A non può trovarsi nella cella x o nella cella y al tempo t".
Applicando il symmetries breaking, le performance dell'algoritmo migliorano considerevolmente.

Si possono aggiungere **admissible heuristics** per migliorare ulteriormente le performance.

Aggiungendo **learned heuristics** le performance migliorano drasticamente, MA si perde l'ottimalità.

### Reduction-based

Si cerca di ridurre il problema, che è NP-hard, ad altro problemi noti per cui si ha una soluzione, ad esempio SAT, integer linear programming e answer set programming.

## Algoritmi subottimali bounded

Un esempio è la FOCAL search, nella quale si può decidere il grado accettabile di subottimalità.

### Relaxing optimal solvers

## Algoritmi subottimali

### Search-based suboptimal solvers

Veloci, facili da capire e implementare MA si perde ottimalità e completezza.

### Cooperative A* ( Prioritized planning)

Per ogni agente si calcola il cammino, che viene riservato. Per l'agente successivo si calcola un percorso che non collida con quelli precedenti.
Non è garantita la completezza.

Il prioritized planning è semplice e veloce. Non da garanzie, ma produce spesso piani di alta qualità.
Purtroppo in diverse situazioni può fallire nel dare una soluzione (stalli). A volte può dare una soluzione, a patto che i cammini degli agenti vengano pianificati in un certo ordine.

### Large neighbourhood search for MAPF

Utilizza un ciclo di azioni: initialize, destroy, repair.

C'è una fase di inizializzazione, dove si assegna ad ogni agente un cammino, cercando di minimizzare il numero di collisioni.

Poi si selezionano i subset di agenti che sono in collisione e si riassegnano cammini cercando sempre di minimizzare i conflitti.

### Procedure-based / rule-based suboptimal solvers

Si ha la completezza, sono molto veloci e possono risolvere problemi grandi, MA sono lontani dall'ottimo.

Si specificano regole di movimento, ad esempio "Muoviti sulla highway".

Un esempio è PUSH, dove si risolvono le collisioni "spingendo" via gli altri agenti ricorsivamente: se stiamo considerando l'agente A e sul suo cammino si trova B, B deve spostarsi e lasciare passare A.
Si tratta di un algoritmo facile e veloce, con un'ottima scalabilità e che può produrre buoni piani MA non è completo, si possono verificare facilmente situazione di stallo, inoltre è solo vagamente "consapevole" dell'obiettivo, può capitare che un agente debba decidere tra più direzioni in cui spostarsi e in quel caso non sa distinguere la scelta buona da quella catastrofica.

Il PUSH operator può essere combinato con altri operators (SWAP, ROTATE, ecc.) per migliorare le prestazioni.