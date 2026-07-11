SELECT *
FROM inventory
WHERE inventory_on_hand < 0
   OR inventory_in_transit < 0;
