load data local infile 'items.csv'
into table item
fields terminated by ',' enclosed by '"' escaped by '\\'
lines terminated by '\n'
(itemId, parentItemId, name, baseItemPrice, salePrice, upc, categoryPath, shortDescription, longDescription, brandName, thumbnailImage, mediumImage, largeImage, productTrackingUrl, freeShipping, ninetySevenCentShipping, standardShipRate, twoThreeDayShippingRate, overnightShippingRate, size, color, availableOnline);
