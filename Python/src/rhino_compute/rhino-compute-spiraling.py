import requests
import json
import rhino3dm
import base64

# === Define Rhino.Compute endpoint ===
URL = "http://localhost:6500/grasshopper"  # Local Rhino Compute server
GH_FILE = r"C:\Users\Miriam\compas_rrc_start\grasshopper\spiraling_camera_path.gh"

with open(GH_FILE, "rb") as f:
    gh_bytes = f.read()
gh_base64 = base64.b64encode(gh_bytes).decode("utf-8")

# Example inputs
centroid = rhino3dm.Point3d(0, 0, 0)
xy_scale = 1.0
z_scale = 1.0
height = 100.0

inputs = [
    {
        "ParamName": "Scan_Centroid",
        "InnerTree": {
            "{ 0; }": [{
                "type": "Point3d",
                "data": f"{centroid.X},{centroid.Y},{centroid.Z}"
            }]
        }
    },
    {
        "ParamName": "Scan_XYScale",
        "InnerTree": {
            "{ 0; }": [{
                "type": "Number",
                "data": str(xy_scale)
            }]
        }
    },
    {
        "ParamName": "Scan_ZScale",
        "InnerTree": {
            "{ 0; }": [{
                "type": "Number",
                "data": str(z_scale)
            }]
        }
    },
    {
        "ParamName": "Scan_Height",
        "InnerTree": {
            "{ 0; }": [{
                "type": "Number",
                "data": str(height)
            }]
        }
    },
    # Axis flipping booleans
    *[
        {
            "ParamName": name,
            "InnerTree": {
                "{ 0; }": [{
                    "type": "Boolean",
                    "data": "false"
                }]
            }
        }
        for name in [
            "Scan1_ReverseXAxis", "Scan1_ReverseYAxis", "Scan1_SwapAxis",
            "Scan2_ReverseXAxis", "Scan2_ReverseYAxis", "Scan2_SwapAxis"
        ]
    ],

    # JSON path and dump settings
    {
        "ParamName": "Scan1_JsonPath",
        "InnerTree": {
            "{ 0; }": [{
                "type": "String",
                "data": "C:\\Users\\Miriam\\scan1.json"
            }]
        }
    },
    {
        "ParamName": "Scan1_JsonDump",
        "InnerTree": {
            "{ 0; }": [{
                "type": "Boolean",
                "data": "true"
            }]
        }
    },
    {
        "ParamName": "Scan2_JsonPath",
        "InnerTree": {
            "{ 0; }": [{
                "type": "String",
                "data": "C:\\Users\\Miriam\\scan2.json"
            }]
        }
    },
    {
        "ParamName": "Scan2_JsonDump",
        "InnerTree": {
            "{ 0; }": [{
                "type": "Boolean",
                "data": "true"
            }]
        }
    }
]

# Full JSON body
payload = {
    "algo": gh_base64,
    "pointer": None,
    "values": inputs
}

# Send POST request
response = requests.post(URL, json=payload)

# Check result
print(response.status_code)
if response.ok:
    print(json.dumps(response.json(), indent=2))
else:
    print("Error:", response.text)