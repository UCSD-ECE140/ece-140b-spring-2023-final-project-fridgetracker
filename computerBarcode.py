# Based off of work at https://note.nkmk.me/en/python-opencv-barcode/
# FridgeTracker Group
# Basic barcode scanning and api usage

import cv2, requests

camera_id = 1   # default value is 0 if you only have one camera
delay = 1
window_name = 'Barcode Detection'

bd = cv2.barcode.BarcodeDetector()
cap = cv2.VideoCapture(camera_id)

barcodes = [0]*5

while True:
    ret, frame = cap.read()
    if ret:
        ret_bc, decoded_info, _, points = bd.detectAndDecode(frame)
        if ret_bc:
            frame = cv2.polylines(frame, points.astype(int), True, (0, 255, 0), 3)
            
            for s, p in zip(decoded_info, points):
                
                # if a valid barcode value is found
                if s:                    
                    # shift data through a 5 element list each time a new barcode is detected, with the newest barcode at index 0
                    # and the oldest at index 4. If a new barcode is detected, the list shifts up by one (data @ index 0 -> index 1),
                    # the barcode previously at index 4 is discarded, and the new barcode is added at index 0
                    for i in reversed(range(len(barcodes))):
                        barcodes[i] = barcodes[i-1]
                    barcodes[0] = s

            # if all elements in the barcodes list are the same (aka the scanner has scanned the same barcode number 5 times in a row)
            if len(set(barcodes)) == 1:
                # retrieve product data from api
                rawdata = requests.get('https://api.barcodelookup.com/v3/products?barcode=%s&key=6zusy8frdfgq2uriti6lu5v74ws6n5' % barcodes[0]).json()
                productdata = rawdata['products'][0]
                
                # display product data
                display = 'Type: ' + productdata['category'].rpartition('>')[-1] + '\nBrand: ' + productdata['brand'] + '\nProduct: ' + productdata['title'] + '\nBarcode: ' + productdata['barcode_number']
                print(display)

                break

        cv2.imshow(window_name, frame)

    if cv2.waitKey(delay) & 0xFF == ord('q'):   # exit loop if the q key is pressed after one second of usage
        break

cv2.destroyWindow(window_name)