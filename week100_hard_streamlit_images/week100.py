import streamlit as st
import csv
import pandas as pd

# put csv file in the same directory as this script
# csv file url: https://frostyfridaychallenges.s3.eu-west-1.amazonaws.com/challenge_100/images.csv

# CSV module has a default field size limit of 131072 bytes (131kb)
VERY_LARGE_SIZE = 200_000_000
csv.field_size_limit(VERY_LARGE_SIZE)

# open csv file
@st.cache_data
def open_csv():
    # convert to dataframe
    result_df = pd.DataFrame(columns=["filename", "image_bytes", "image_hex_head"])

    with open("images.csv", "r", encoding="utf8") as f:
        reader = csv.reader(f)

        # skip header
        header = next(reader)
        print("DEBUG: {}".format(header))

        arr_filename = []
        arr_image_bytes = []
        arr_image_hex_head = []
        for row in reader:
            # read first column as filename
            filename = row[0]
            arr_filename.append(filename)
            # read second column, and convert from hex string to bytes
            hex_string = row[1]
            image_bytes = bytes.fromhex(hex_string)
            arr_image_bytes.append(image_bytes)
            arr_image_hex_head.append(hex_string[:32])

        # add to dataframe
        result_df = pd.DataFrame({
            "filename": arr_filename,
            "image_bytes": arr_image_bytes,
            "image_hex_head": arr_image_hex_head
        })

    return result_df

# Main function
def main():
    # open csv file
    df = open_csv()

    # display as dataframe
    df_to_show = df.loc[:, ["filename", "image_hex_head"]]
    # and select row
    event = st.dataframe(df_to_show, on_select="rerun", selection_mode="single-row")

    # check selection
    if len(event.selection.rows) <= 0:
        st.stop()

    # display image
    row = event.selection.rows[0]
    st.write("filename: ", df.loc[row, "filename"])
    st.image(df.loc[row, "image_bytes"], use_column_width=True)

if __name__ == "__main__":
    main()
