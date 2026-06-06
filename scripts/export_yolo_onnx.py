from ultralytics import YOLO

model = YOLO("yolov8n-pose.pt")
model.export(format="onnx", opset=12, simplify=True, dynamic=False, imgsz=640)
print("Exported to yolov8n-pose.onnx")