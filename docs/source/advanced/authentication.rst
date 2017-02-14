==============
Authentication
==============

Starting from version 0.5, django-modern-rpc supports authentication process. It is possible to restrict access to any
RPC method depending on conditions names "predicate".

Basic principles
================

To provide authentication features, django-modern-rpc introduce the concept of "predicate". A predicate is a python
function taking a request as argument and returning a boolean. The predicate is then associated with a RPC method to
control if its access is allowed depending on the information found in the incoming  request.

[TBD code example needed (bot access restriction ?)]


