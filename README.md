# Mizu: The RESTful Drink Server
![GitHub](https://img.shields.io/github/license/zthart/mizu.svg) 
![pyVersion](https://img.shields.io/badge/python-3.7-blue.svg)

Mizu is the only _debatably-modern_ Drink Server written in Python using Flask, ideal for consumption by CSHers

![A recruiter told me once their co-worker found this reference funny, so I'm rolling with it](https://user-images.githubusercontent.com/4873335/55663141-d2ab9480-57e8-11e9-8a2d-472a0a3994ed.jpg)


Mizu (水) is the Japanese Kanji meaning water. Water is clean and clear, and so too have we strived for clarity in
this implementation of the drink server. Out with websockets and the Sunday protocol, in with a simple and clean
implementation for the core of a project that has been a defining feature of the Computer Science House at RIT in
various forms for more than two decades.

## Documentation

Developer documentation is hosted on Postman and can be found
[here](https://documenter.getpostman.com/view/6712720/S1EJWLQW). Please keep in mind that this project is in development
and the documentation may drift in and out of date. We will make an effort to keep it consistent with the current
functionality of the server.

## Related Projects

- [Potion Seller](https://github.com/ramzallan/potion-seller) - A lightweight RESTful application for controlling the
  CSH Drink Machines
- [Tonic](https://github.com/ramzallan/tonic) - A modern web application to allow users to drop drinks from the CSH
  Drink Machines

## Why it exists
I know you're all disappointed that _yet another_ house service has been written in Python using Flask. I will be the
first to say that **I'm sorry for this**. However, It's become apparent to me in my years of being a drink admin that
there needed to be an infrastructure in drink that took a stab at putting the project in a place where we could stop
worrying about whether or not the server could be moved to a 64-bit machine (drinkjs64 lives on only in our memories,
now), or whether it would work with the new user management infrastructure, or whether the webclient should expose the 
public api to sub-clients, etc.

There were many things that were aging and dying in the previous technology, and replacements have been grafted into the
system time and time again. Drink rewrites have been achieved in the past, but hopefully this one sticks.

## When it will be done
Any drink admin will tell you that this project is never complete. This implementation will be finished and in place
when it outperforms the current implementation.

