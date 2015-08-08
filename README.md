# yowlayer-store
This is a storage layer for yowsup. The aim is to add this layer right above the protocol layers, and then it would store
what it finds appropriate from the incoming data from lower layers, and outgoing data from upper layers.

## Status

This is still work in progress. Contributions are welcomed!

### Milestone 0:

The layer should passively store the data as described. There is no way to interact with the layer yet,
for example to retrieve old messages.


### Milestone 1:

A layer interface. This is another WIP yowsup feature which allow layers to expose some interface for other to interact with them.
Details about the Store interface will come later.

 ## License

 GPLv3