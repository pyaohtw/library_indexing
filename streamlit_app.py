import streamlit as st 
import pandas as pd
import datetime

# Load the index data from the CSV file
index_df = pd.read_csv('index.csv')

# Create a sample dataframe for well structure (8 rows x 12 columns)
data = [[f'{chr(65 + row)}{col + 1}' for col in range(12)] for row in range(8)]
df = pd.DataFrame(data, columns=[f'A{i + 1}' for i in range(12)])

# Apply CSS styling for cell buttons
st.markdown(
    """
    <style>
    /* Styling for cell buttons */
    .stButton button {
        width: 60px;
        height: 40px;
        text-align: center;
        vertical-align: middle;
    }

    /* Increase the width of the sidebar */
    .css-1d391kg {
        width: 600px !important;  /* Adjust sidebar width as needed */
    }

    /* Adjust the matrix width inside the sidebar with small left margin */
    #matrix-container {
        max-width: 400px !important;  /* Adjust this value as needed for the matrix in sidebar */
        margin-left: 10px;  /* Set a small left margin */
        margin-right: auto;
    }

    /* Make the font smaller in the matrix to fit the sidebar */
    #matrix-container td, #matrix-container th {
        font-size: 22px !important;  /* Adjust the font size to make it smaller */
        padding: 5px;  /* Optional: Reduce padding to save space */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state for user selections
if 'end_cell' not in st.session_state:
    st.session_state.end_cell = None
if 'i5_row' not in st.session_state:
    st.session_state.i5_row = None
if 'i7_col' not in st.session_state:
    st.session_state.i7_col = None
if 'removal_wells' not in st.session_state:
    st.session_state.removal_wells = []

# Initialize selected_data as an empty list if end_cell is not yet selected
selected_data = []

# Function to get the selection based on the end cell
def get_selection(end_cell):
    row_index = ord(end_cell[0]) - 65  # Convert letter to row index (A=0, B=1, ..., H=7)
    col_index = int(end_cell[1:]) - 1   # Convert column number to index (1=0, 2=1, ..., 12=11)
    
    # Create a selection up to the end cell
    selection = []
    for r in range(row_index + 1):
        for c in range(col_index + 1):
            selection.append(df.iloc[r, c])
    return selection

# Streamlit app layout
st.title("App Summary")
st.write("This app is designed to assign i7 and i5 indices to your samples in a 96-well format.")
st.title("Well Selector")
st.write("Select a well to generate a matrix from A1 to the selected well.")
st.write("Your selected data matrix is displayed in the sidebar. If you don't see the full matrix, adjust the sidebar's size or position for optimal viewing.")

# Create buttons for each cell in a grid format
for i in range(df.shape[0]):
    cols = st.columns(df.shape[1])  # Create a row of columns
    for j in range(df.shape[1]):
        cell_value = df.iloc[i, j]
        
        # Create a button for each cell
        if cols[j].button(cell_value, key=cell_value, help=f"Select {cell_value}"):
            st.session_state.end_cell = cell_value  # Update the selected cell

# Check if an end cell has been selected
if st.session_state.end_cell:
    selected_data = get_selection(st.session_state.end_cell)  # Ensure selected_data is defined

# Remove Wells from Output (Multiple Selection)
st.subheader("Remove Wells from Output (Optional)")
st.write("Select wells to exclude from the output. To undo changes, simply refresh the page.")

for i in range(df.shape[0]):
    cols = st.columns(df.shape[1], gap="small")
    for j in range(df.shape[1]):
        cell_value = df.iloc[i, j]
        if cell_value not in st.session_state.removal_wells:
            if cols[j].button(cell_value, key=f"remove_{cell_value}", help=f"Remove {cell_value}"):
                st.session_state.removal_wells.append(cell_value)  # Add to removal list
        else:
            cols[j].markdown(f"""
                <div style="color: red; font-weight: bold; display: flex; justify-content: center; align-items: center; height: 100%; width: 100%; text-align: center;">
                    {cell_value}
                </div>
            """, unsafe_allow_html=True)

# In your sidebar, wrap the matrix display in a div with id="matrix-container"
with st.sidebar:
    st.title("Final Selected Data Matrix")
    final_matrix = df.copy()

    # Exclude the wells marked for removal from the display
    for i in range(df.shape[0]):
        for j in range(df.shape[1]):
            cell_value = df.iloc[i, j]
            if cell_value in st.session_state.removal_wells:
                final_matrix.iloc[i, j] = ''  # Clear out removed wells
            elif cell_value in selected_data:
                final_matrix.iloc[i, j] = f'<span style="background-color:yellow; font-weight:bold; color:black;">{cell_value}</span>'
            else:
                final_matrix.iloc[i, j] = f'<span>{cell_value}</span>'

    # Wrap the matrix in a div with id="matrix-container"
    st.markdown(f'<div id="matrix-container">{final_matrix.to_html(escape=False, index=False, header=False)}</div>', unsafe_allow_html=True)

# Dropdowns for i5 and i7 selections
st.subheader("Select i7 Column and i5 Row")
i7_col = st.selectbox("Select i7 Column", list(range(1, 13)))
i5_row = st.selectbox("Select i5 Row", ["A", "B", "C", "D", "E", "F", "G", "H"])

# Create a DataFrame for horizontal output
output_data = []

# Populate the output_data based on selected wells
for i in range(len(selected_data)):
    well = selected_data[i]
    if well not in st.session_state.removal_wells:  # Skip removed wells
        well_row = well[0]
        well_number = int(well[1:])
        
        # Fetch i5 value and i7 value (same logic as before)
        i5_value = f"{i5_row}{well_number}"
        i5_row_data = index_df.loc[index_df['index'] == i5_value, ['i5-name', 'i5-index']].values[0]
        
        i7_value = f"{well_row}{i7_col}"
        i7_row_data = index_df.loc[index_df['index'] == i7_value, ['i7-name', 'i7-index']].values[0]
        
        # Append the output row for horizontal display
        output_data.append({
            "Well": well,
            "i7-name": i7_row_data[0],
            "i7-index": i7_row_data[1],
            "i5-name": i5_row_data[0],
            "i5-index": i5_row_data[1]
        })

# Generate timestamp in the format day_month_year_min_sec
timestamp = datetime.datetime.now().strftime("%D_%M%S")

# Prefix input box
prefix = st.text_input("Enter a prefix for Sample_ID (optional)", value="")

# Generate horizontal output
output_data = []
for i in range(8):
    for j in range(12):
        well = df.iloc[i, j]
        if well in selected_data and well not in st.session_state.removal_wells:
            i5_value = f"{i5_row}{j + 1}"
            i5_data = index_df.loc[index_df['index'] == i5_value, ['i5-name', 'i5-index']].values[0]
            i7_value = f"{chr(65 + i)}{i7_col}"
            i7_data = index_df.loc[index_df['index'] == i7_value, ['i7-name', 'i7-index']].values[0]
            
            # Apply prefix
            sample_id = f"{prefix}{well}" if prefix else well
            
            output_data.append({"Sample_ID": sample_id, "Sample_name": "", "i7-name": i7_data[0], "i7-index": i7_data[1], "i5-name": i5_data[0], "i5-index": i5_data[1]})

# Generate vertical output
vertical_output_data = []
rows = [f"{chr(65 + r)}{c + 1}" for c in range(12) for r in range(8)]
for well in rows:
    if well in selected_data and well not in st.session_state.removal_wells:
        well_row = well[0]
        well_number = int(well[1:])
        i5_value = f"{i5_row}{well_number}"
        i5_row_data = index_df.loc[index_df['index'] == i5_value, ['i5-name', 'i5-index']].values[0]
        i7_value = f"{well_row}{i7_col}"
        i7_row_data = index_df.loc[index_df['index'] == i7_value, ['i7-name', 'i7-index']].values[0]
        
        # Apply prefix
        sample_id = f"{prefix}{well}" if prefix else well
        
        vertical_output_data.append({
            "Sample_ID": sample_id,
            "Sample_name": "",
            "i7-name": i7_row_data[0],
            "i7-index": i7_row_data[1],
            "i5-name": i5_row_data[0],
            "i5-index": i5_row_data[1]
        })

# Convert to DataFrame
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
output_df = pd.DataFrame(output_data)
vertical_output_df = pd.DataFrame(vertical_output_data)

# Download buttons
st.download_button("Download Horizontal Output as CSV", data=output_df.to_csv(index=False), file_name=f"horizontal_output_{timestamp}.csv", mime="text/csv")
st.write("### Horizontal Output →")
st.dataframe(output_df)

st.download_button("Download Vertical Output as CSV", data=vertical_output_df.to_csv(index=False), file_name=f"vertical_output_{timestamp}.csv", mime="text/csv")
st.write("### Vertical Output ↓")
st.dataframe(vertical_output_df)
