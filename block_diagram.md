
## Block Diagram


+------------------+         +------------------+        +------------------+         +------------------+
|  Ground Laptop   | <-----> |  Ground Heltec   | <====> |   Air Heltec     | <-----> |    Air Laptop     |
|  ground_hmi.py   |  USB    |   LoRa Bridge    |  LoRa  |    LoRa Bridge   |   USB   |    air_hmi.py     |
+------------------+         +------------------+        +------------------+         +------------------+