import cv2
#from Main import dist

def dist(a , b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

class TrackedObject:
    def __init__(self, contour):
        self.contour = contour
        (x, y, w, h) = cv2.boundingRect(contour)
        self.boundingRect = (x, y, w, h)

        center_x = x + (w >> 2)
        center_y = y + (h >> 2)

        self.centers = list()
        self.centers.append([center_x, center_y])

        self.next = [center_x, center_y]

        self.diagonal = dist((0, w), (0, h))
        self.aspect_ratio = 1.0 * w / h

        self.need = True
        self.found = True

        self.not_found_cnt = 0

        self.sgnneg = False
        self.sgnpos = False


    def check_crossing(self, a, b):
        if (self.sgnneg and self.sgnpos) == True:
            return 0
    #    if (self.sgnneg == True) and (self.sgnneg == True):
    #        return 0
        center = self.centers[len(self.centers) - 1]
        A = (a[1] - b[1])
        B = (b[0] - a[0])
        C = (a[0] * b[1] - a[1] * b[0])
        val = center[0] * A + center[1] * B + C
        self.sgnpos = self.sgnpos or (val >= 0)
        self.sgnneg = self.sgnneg or (val <= 0)
        if self.sgnneg and self.sgnpos:
            return 1
        else:
            return 0


    def predict_next(self):
        tot = len(self.centers)

        if tot == 1:
            x = self.centers[tot - 1][0]
            y = self.centers[tot - 1][1]
        elif tot == 2:
            dX = self.centers[tot - 1][0] - self.centers[tot - 2][0]
            dY = self.centers[tot - 1][1] - self.centers[tot - 2][1]

            x = self.centers[tot - 1][0] + dX
            y = self.centers[tot - 1][1] + dY
        elif tot == 3:
            sumX = (2 * (self.centers[tot - 1][0] - self.centers[tot - 2][0])) + (self.centers[tot - 2][0] - self.centers[tot - 3][0])
            dX = int(sumX / 3)

            sumY = (2 * (self.centers[tot - 1][1] - self.centers[tot - 2][1])) + (self.centers[tot - 2][1] - self.centers[tot - 3][1])
            dY = int(sumY / 3)

            x = self.centers[tot - 1][0] + dX
            y = self.centers[tot - 1][1] + dY
        else:
            sumX = (3 * (self.centers[tot - 1][0] - self.centers[tot - 2][0])) + 2 * (self.centers[tot - 2][0] - self.centers[tot - 3][0]) + (self.centers[tot - 3][0] - self.centers[tot - 4][0])
            dX = int(sumX / 6)

            sumY = (3 * (self.centers[tot - 1][1] - self.centers[tot - 2][1])) + 2 * (self.centers[tot - 2][1] - self.centers[tot - 3][1]) + (self.centers[tot - 3][1] - self.centers[tot - 4][1])
            dY = int(sumY / 6)

            x = self.centers[tot - 1][0] + dX
            y = self.centers[tot - 1][1] + dY

        self.next = (x, y)

