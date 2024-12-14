import xml.etree.ElementTree as ET
from io import BytesIO
from datetime import timedelta
from typing import Dict, ByteString, Tuple
from dateutil import parser

namespaces = {
    "ns2": "http://www.garmin.com/xmlschemas/ActivityExtension/v2",  # Namespace for extensions
}


def convert_tcx_in_memory(input_data: ByteString) -> Tuple[ByteString, Dict]:
    """
    Converts TCX data in memory without saving to a file and extracts summary data.
    :param input_data: TCX data as bytes (e.g., from a downloaded file).
    :return: Converted TCX data as bytes and a dictionary with summary data.
    """

    # Parse the input data
    tree = ET.ElementTree(ET.fromstring(input_data))
    root = tree.getroot()

    # Extract summary data
    summary_data = {}
    activities = root.findall(
        ".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Activity"
    )
    if activities:
        activity = activities[0]  # Assuming only one activity for simplicity
        # Extract activity ID (date and time)
        activity_id = activity.find(
            ".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Id"
        )
        if activity_id is not None and activity_id.text:
            # Parse the datetime and format it in a human-readable way
            activity_datetime = parser.isoparse(activity_id.text)
            summary_data["activity_datetime"] = activity_datetime.strftime(
                "%d %b @ %H:%M UTC"
            )

        # Extract total time in seconds
        total_time_seconds = activity.find(
            ".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}TotalTimeSeconds"
        )
        if total_time_seconds is not None and total_time_seconds.text:
            total_seconds = float(total_time_seconds.text)
            # Round the total time to the nearest second
            total_seconds_rounded = round(total_seconds)
            summary_data["total_time"] = str(
                timedelta(seconds=total_seconds_rounded)
            )

        # Extract total distance in meters
        distance_meters = activity.find(
            ".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}DistanceMeters"
        )
        if distance_meters is not None and distance_meters.text:
            distance_km = float(distance_meters.text) / 1000
            summary_data["total_distance_km"] = f"{distance_km:.2f}"

    # Create a new root for the output TCX
    new_root = ET.Element(
        "TrainingCenterDatabase",
        {
            "xsi:schemaLocation": "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd",
            "xmlns:ns2": namespaces["ns2"],  # Namespace for extensions
            "xmlns": "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2",  # Default namespace
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        },
    )

    activities_out = ET.SubElement(new_root, "Activities")

    # Transfer information for each activity
    for activity in activities:
        # Convert the 'Sport' attribute value
        sport = activity.attrib["Sport"].capitalize()

        activity_out = ET.SubElement(activities_out, "Activity", Sport=sport)

        # Transfer activity ID
        activity_id = activity.find(
            ".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Id"
        )
        if activity_id is not None:
            ET.SubElement(activity_out, "Id").text = activity_id.text

        # Transfer information for each lap
        for lap in activity.findall(
            ".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Lap"
        ):
            lap_out = ET.SubElement(
                activity_out, "Lap", StartTime=lap.attrib["StartTime"]
            )

            # Transfer main lap data
            for element in [
                "TotalTimeSeconds",
                "DistanceMeters",
                "Calories",
                "Intensity",
                "TriggerMethod",
            ]:
                elem = lap.find(
                    f".//{{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}}{element}"
                )
                if elem is not None:
                    ET.SubElement(lap_out, element).text = elem.text

            # Process track and trackpoint data
            track_out = ET.SubElement(lap_out, "Track")
            for trackpoint in lap.findall(
                ".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Trackpoint"
            ):
                trackpoint_out = ET.SubElement(track_out, "Trackpoint")

                # Transfer time and distance
                for element in ["Time", "DistanceMeters"]:
                    elem = trackpoint.find(
                        f".//{{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}}{element}"
                    )
                    if elem is not None:
                        ET.SubElement(trackpoint_out, element).text = elem.text

                # Transfer heart rate
                heart_rate = trackpoint.find(
                    ".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}HeartRateBpm"
                )
                if heart_rate is not None:
                    heart_rate_out = ET.SubElement(
                        trackpoint_out, "HeartRateBpm"
                    )
                    value = heart_rate.find(
                        ".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Value"
                    )
                    if value is not None:
                        ET.SubElement(heart_rate_out, "Value").text = value.text

                # Transfer cadence
                cadence = trackpoint.find(
                    ".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Cadence"
                )
                if cadence is not None:
                    ET.SubElement(trackpoint_out, "Cadence").text = cadence.text

                # Transfer extension data (speed, watts, etc.)
                extensions = trackpoint.find(
                    ".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Extensions"
                )
                if extensions is not None:
                    ax_extension = extensions.find(
                        ".//{http://www.garmin.com/xmlschemas/ActivityExtension/v2}TPX"
                    )
                    if ax_extension is not None:
                        tpx_out = ET.SubElement(trackpoint_out, "Extensions")
                        ax_tpx_out = ET.SubElement(
                            tpx_out,
                            f"{{{namespaces['ns2']}}}TPX",
                        )
                        for ext_element in ["Speed", "Watts"]:
                            ext = ax_extension.find(
                                f".//{{http://www.garmin.com/xmlschemas/ActivityExtension/v2}}{ext_element}"
                            )
                            if ext is not None:
                                ET.SubElement(
                                    ax_tpx_out,
                                    f"{{{namespaces['ns2']}}}{ext_element}",
                                ).text = ext.text

    # Serialize the new XML tree to bytes
    output_data = BytesIO()
    tree_out = ET.ElementTree(new_root)
    tree_out.write(output_data, xml_declaration=True, encoding="UTF-8")
    return output_data.getvalue(), summary_data
