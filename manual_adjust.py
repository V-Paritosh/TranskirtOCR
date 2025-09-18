import cv2
import numpy as np
import json

class CornerSelector:
  def __init__(self, image, pts):
    self.original_image = image.copy()
    self.zoom = 1.0
    self.offset = np.array([0, 0])
    self.drag_start = None
    self.dragging = False

    self.image = image.copy()
    self.clone = image.copy()
    self.pts = pts.astype(int)
    self.selected_pt = None
    self.radius = 10

    cv2.namedWindow("Adjust Corners")
    cv2.setMouseCallback("Adjust Corners", self.mouse_events)

  def transform_coords(self, x, y):
    return int((x - self.offset[0]) / self.zoom), int((y - self.offset[1]) / self.zoom)

  def mouse_events(self, event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
      tx, ty = self.transform_coords(x, y)
      for i, pt in enumerate(self.pts):
        if np.linalg.norm(pt - np.array([tx, ty])) < self.radius:
          self.selected_pt = i
          break

    elif event == cv2.EVENT_MOUSEMOVE:
      if self.selected_pt is not None:
        tx, ty = self.transform_coords(x, y)
        self.pts[self.selected_pt] = [tx, ty]
      elif self.dragging:
        dx, dy = x - self.drag_start[0], y - self.drag_start[1]
        self.offset += np.array([dx, dy])
        self.drag_start = (x, y)

    elif event == cv2.EVENT_LBUTTONUP:
      self.selected_pt = None

    elif event == cv2.EVENT_RBUTTONDOWN:
      self.dragging = True
      self.drag_start = (x, y)

    elif event == cv2.EVENT_RBUTTONUP:
      self.dragging = False

    elif event == cv2.EVENT_MOUSEWHEEL:
      if flags > 0:
        self.zoom *= 1.1
      else:
        self.zoom /= 1.1

  def draw(self):
    resized = cv2.resize(self.original_image, (0, 0), fx=self.zoom, fy=self.zoom)
    canvas = resized.copy()
    self.clone = canvas

    for pt in self.pts:
      zoomed_pt = (pt * self.zoom + self.offset).astype(int)
      cv2.circle(canvas, tuple(zoomed_pt), self.radius, (0, 0, 255), -1)

    zoomed_pts = (self.pts * self.zoom + self.offset).astype(int)
    cv2.polylines(canvas, [zoomed_pts], isClosed=True, color=(0, 255, 0), thickness=2)

    cv2.imshow("Adjust Corners", canvas)

  def run(self):
    while True:
      self.draw()
      key = cv2.waitKey(10) & 0xFF
      if key == 13 or key == 10 or key == ord('q'):  # ENTER or 'q'
        break
      elif key == ord('s'):
        np.save("adjusted_corners.npy", self.pts)
        with open("adjusted_corners.json", "w") as f:
          json.dump(self.pts.tolist(), f)
        print("Saved corner points.")

    cv2.destroyWindow("Adjust Corners")
    return self.pts.astype("float32")
