# Tirocinio

Il lavoro svolto verte sullo studio del problema del MAPF: Multi-Agent Path Finding e allo sviluppo di algoritmi per risolvere delle sue varianti.

Il problema consiste nel pianificare i percorsi di movimento per agenti (ad esempio, robot in un magazzino automatizzato) che devono spostarsi da un punto di partenza ad uno di arrivo, detto anche di goal, senza scontrarsi con ostacoli o tra di loro.

Essendo un problema complesso, non esiste un'unica soluzione elementare per risolverlo, ma ci sono piuttosto diversi approcci: è possibile risolvere il problema in modo ottimo, sacrificando però le performance quando il numero di agenti coinvolti inizia a crescere, oppure puntare ad una soluzione sub-ottimale, ma che si possa ottenere in tempo ragionevole per un numero più elevato di agenti.

## Studio algoritmi MAPF

### Definizione problema

Quando si affronta un problema di MAPF bisogna innanzitutto decidere come formulare il problema.

Un primo aspetto fondamentale riguarda la definizione di ciò che costituisce un conflitto: esistono infatti diversi tipi di conflitto tra agenti e alcuni posso essere accettati in un problema, mentre altri no.  
Solitamente vengono proibiti i conflitti di vertice, in cui due agenti si trovano nello stesso nodo allo stesso tempo, e i conflitti di edge, dove due agenti tentano di attraversare lo stesso arco allo stesso tempo in direzioni opposte (swap).

Bisogna scegliere se il tempo è discreto o continuo.  
Normalmente si assume un tempo discreto, in cui ogni agente in un time step può compiere esattamente un'azione, sia essa di movimento o di attesa.

Va determinato in quante direzioni possono muoversi gli agenti.  
In un problema standard un agente può muoversi in una delle quattro direzioni cardinali, di una casella, perciò ogni movimento richiede esattamente un time step.
In presenza di pattern di movimento più complessi però, un'azione potrebbe richiedere più tempo di un'altra, e quindi si richiederebbe una formulazione del tempo non discreta.

Un'altra variabile è la dimensione e la forma degli agenti.
Solitamente tutti gli agenti hanno la stessa forma e dimensione, ma se alcuni agenti sono più grossi di altri o hanno forme particolari, potrebbero verificarsi nuovi tipi di conflitto, anche tra agenti in vertici apparentemente lontani.

Può variare anche il comportamento dell'agente una volta raggiunto il suo goal.  
L'assunzione standard è lo "stay at target" per cui l'agente smette di muoversi, mentre il "disappear at target" assume che l'agente lasci la casella libera e "sparisca" una volta raggiunto il suo obiettivo.  
C'è poi una variante del problema di MAPF dove, una volta raggiunto un goal, ne viene assegnato un altro, oppure l'agente ha una lista di goal da raggiungere, in un ordine fisso o variabile.

### Algoritmi di MAPF

## Problema dell'agent meeting

Una variante interessante del MAPF problem è quella in cui gli agenti non devono semplicemente spostarsi da un punto A di partenza ad un punto B di goal, ma hanno invece un insieme comune di punti di goal, e l'importante è che ogni agente arrivi ad occupare uno di quei punti, senza badare a quale va dove.

Sebbene possa sembrare una versione più semplice del problema, la difficoltà aggiuntiva diventa evidente illustrando la seconda caratteristica di questa variante: i punti di goal che gli agenti devono andare a raggiungere non sono prestabiliti, ma vengono determinati facendo in modo che rispettino delle caratteristiche.  
Una volta arrivati ai goal, gli agenti devono essere tutti connessi tra di loro, oppure si può decidere che un agente può avere al massimo n agenti intermediari, tramite i quali è connesso alla totalità degli altri agenti.  
Due agenti sono connessi se i vertici che occupano sono connessi su un grafo di connessione costruito a partire dal grafo primario, utilizzando una definizione di connessione.  
Questo generalmente significa che gli agenti dovranno andare ad incontrarsi in punti vicini tra di loro e che non presentino ostacoli che si staglino tra loro.  
Per decidere quale agente si deve dirigere ad uno dei goal determinati si possono considerare opzioni, una di queste puù essere tentare di far raggiungere un goal all'agente più vicino ad esso, in modo da minimizzare il costo del suo cammino.  
In ogni caso si assume che ogni vertice del grafo primario sia connesso ad ogni altro vertice di tale grafo, così non si considerano grafi degeneri in cui ci siano zone non raggiungibili, in quanto tali grafi avrebbero difficilmente applicazione in contesti utili del mondo reale.  
Tale assunzione ovviamente non vale per il grafo di connessione, dove vertici lontani tra loro, o tra i quali sono piazzati diversi ostacoli non permettono la comunicazione tra agenti.

Il requisito di connessione ha un corrispettivo in situazioni reali tali per cui gli agenti devono poter comunicare tra di loro, ad esempio in un magazzino automatizzato i robot potrebbero avere il compito di monitorarsi a vicenda, per controllare il loro funzionamento sia corretto.

### Algoritmo da me sviluppato

Per prima cosa prendo in esame un'istanza di problema, cioè una mappa, definita dalle sue dimensioni (lunghezza e larghezza) e dalla posizione degli ostacoli, e le posizioni di partenza e di goal degli agenti.

A questo punto genero il grafo di connessione a partire dalla mappa, utilizzando una definizione di connessione.
L'assunzione più semplice è che tutti i vertici siano connessi, ma ciò è inutile; una definizione più interessante è basata sulla distanza: se due vertici hanno una distanza minore di un certo parametro, allora sono connessi.
Una definizione più complessa combina la distanza tra vertici e gli ostacoli posti tra loro: due vertici sono connessi se tra loro la distanza è minore di un certo parametro, e la distanza è considerata maggiore se ci sono ostacoli sulla linea immaginaria che li congiunge.
Ciò cerca di simulare un segnale wireless che si indebolisce se deve passare attraverso superfici solide.

Se si considerano gli ostacoli tra due vertici per determinarne la connessione, ho fatto in modo che un ostacolo abbia un peso maggiore se blocca totalmente la linea diretta che li congiunge, mentre ha un peso ridotto se la linea passa solo parzialmente attraverso esso.
In questo modo si può simulare meglio l'indebolimento del segnale, che sarà maggior all'aumentare della massa solida da attraversare.

Successivamente utilizzo il grafo di connessione creato per trovare n goal (dove n è il numero di agenti) che rispettino le condizioni stabilite, quindi che siano o tutti connessi, oppure connessi tramite al massimo k intermediari.
Posso servirmi delle posizioni di partenza per cercare di trovare un gruppo di vertici vicino agli agenti.

Il passo successivo consiste nell'assegnare ogni goal ad un agente.
Posso farlo in modo arbitrario, oppure cercando di minimizzare il costo del percorso di ogni agente, oppure il costo medio per tutti gli agenti.

Infine, avendo una mappa, delle posizioni di partenza e di goal, posso passare l'istanza modificata del problema ad un risolutore che utilizzi l'algoritmo CBS, e ottenere così una soluzione al problema.

**Tabella riassuntiva**:

<table>
    <tr>
        <th>Aspetto algoritmo</th>
        <th>Opzioni</th>
    </tr>
    <tr>
        <td>
            Definizione connettività
        </td>
        <td>
            <ul>
                <li><b>Connessione totale</b>: tutti i nodi sono connessi tra loro</li>
                <li><b>Distanza</b>: due nodi sono connessi se non più distanti di un parametro d</li>
                <li><b>Distanza ed ostacoli</b>: due nodi sono connessi se non più distanti di un parametro d.<br>
                La distanza è considerata aumentata se tra loro ci sono ostacoli.<br>
                Un ostacolo che copre pienamente il segmento che li unisce (sul quale viene calcolata la distanza) pesa più di uno che lo copre parzialmente</li>
            </ul>
        </td>
    </tr>
    <tr>
        <td>
            Scelta dei goal
        </td>
        <td>
            <ul>
                <li><b>Random</b>: i nodi di goal sono scelti rispettando solamente il requisito di connettività </li>
                <li><b>Distanza minima</b>: i nodi di goal sono scelti rispettando il requisito di connettività, ma anche cercando nodi che siano il meno distanti possibile dagli agenti</li>
            </ul>
        </td>
    </tr>
    <tr>
        <td>
            Requisito di connettività
        </td>
        <td>
           <ul>
                <li><b>Tutti connessi</b>: tutti gli agenti, giunti ai nodi di goal, devono essere connessi tra loro</li>
                <li><b>Connessione indiretta</b>: giunti ai nodi di goal, gli agenti non devono necessariamente essere tutti connessi tra loro direttamente.<br>
                Un agente A riesce a comunicare con un agente B anche se entrambi sono connessi ad un agente C, senza che A e B lo siano direttamente tra loro</li>
           </ul>
        </td>
    </tr>
    <tr>
        <td>
            Assegnamento dei goal
        </td>
        <td>
            <ul>
                <li><b>Random</b>: i nodi di goal sono assegnati agli agenti in modo arbitrario</li>
                <li><b>Distanza minima</b>: utilizzando un approccio greedy, si cerca di assegnare ogni nodo di goal all'agente che si trova più vicino ad esso</li>
            </ul>
        </td>
    </tr>
</table>

Passando il problema modificato al risolutore CBS si è verificata un'anomalia con l'istanza `/instances/test_1.txt`.
L'algoritmo permetteva ad alcuni agenti di collidere tra loro.

A parte questo strano comportamento, si può notare come modificando l'istanza del problema con l'algoritmo sviluppato, il CBS impieghi meno tempo per trovare una soluzione.
Ci sono delle eccezioni: istanze difficili per il quale l'algoritmo CBS impiega centinaia o migliaia di iterazioni per trovare una soluzione accettabile.

#### Statistiche

Per quanto riguarda la somma dei costi dei cammini, si può verificare come generando nuovi nodi di goal tramite l'algoritmo creato, la somma dei costi in media diminuisca.
Su 50 test, solo in 6 casi hanno un costo totale minore i cammini con i goal originari, più 3 casi in cui con i nuovi goal l'algoritmo non termina in un tempo ragionevole.
Negli altri 41 casi, il nuovo problema ha una soluzione con costo totale inferiore e spesso non di poco.