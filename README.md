# Mizu: The RESTful Drink Server

Mizu (水) is the Japanese Kanji meaning water. Water is clean and clear, and so too have we strived for clarity in
this implementation of the drink server. Out with websockets and the Sunday protocol, in with a simple and clean
implementation for the core of a project that has been a defining feature of the Computer Science House at RIT in
various forms for more than two decades.

## Why it exists
I know you're all disappointed that _yet another_ house service has been written in Python using Flask. I will be the
first to say that **I'm sorry for this**. However, It's become apparent to me in my years of being a drink admin that
there needed to be an infrastructure in drink that took a stab at putting the project in a place where we could stop
worrying about whether or not the server could be moved to a 64-bit machine (drinkjs64 lives on only in our memories,
now), or whether it would work with the new user management infrastructure, or whether the webclient should expose the 
public api to sub-clients, etc.

There were many things that were aging and dying in the previous technology, and replacements have been grafted into the
system time and time again. Drink rewrites have been achieved in the past, but hopefull this one sticks.

## When it will be done
Any drink admin will tell you that this project is never complete. This implementation will be finished and in place
when it outperforms the current implementation.

