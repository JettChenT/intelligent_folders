# This generates the plist file
import sys
from pathlib import Path

service_loc = Path(__file__).parent.parent / "service.py"

PLST = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>me.jettchen.forg</string>

    <key>OnDemand</key>
    <false/>

    <key>UserName</key>
    <string>user</string>

    <key>GroupName</key>
    <string>utilities</string>

    <key>ProgramArguments</key>
    <array>
            <string>{sys.executable}</string>
            <string>{service_loc}</string>
    </array>
</dict>
</plist>"""