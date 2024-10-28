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
    .stButton button {
        width: 60px;
        height: 50px;
        text-align: center;
        vertical-align: middle;
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
st.title("Interactive Cell Selector")

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
    st.subheader("Selected Data")
    selected_data = get_selection(st.session_state.end_cell)

    # Display entire matrix with highlighted selected range
    styled_matrix = df.copy()
    for i in range(df.shape[0]):
        for j in range(df.shape[1]):
            cell_value = df.iloc[i, j]
            # Highlight the cells within the selected range
            if cell_value in selected_data:
                styled_matrix.iloc[i, j] = f'<span style="background-color:yellow; font-weight:bold; color:black;">{cell_value}</span>'
            else:
                styled_matrix.iloc[i, j] = f'<span>{cell_value}</span>'
                
    # Display the styled matrix with HTML
    st.markdown(styled_matrix.to_html(escape=False, index=False, header=False), unsafe_allow_html=True)

    # Dropdowns for i5 and i7 selections
    st.subheader("Select i5 Row and i7 Column")
    i5_row = st.selectbox("Select i5 Row", ["A", "B", "C", "D", "E", "F", "G", "H"])
    i7_col = st.selectbox("Select i7 Column", list(range(1, 13)))

    # Prepare the DataFrame to hold the output data
    output_data = []

    # Calculate how many wells will be populated based on the selected wells
    total_cells = len(selected_data)

    # Append i5 and i7 values based on the user selections
    for i in range(total_cells):
        well = selected_data[i]
        well_row = well[0]  # Extract the letter (A, B, C, etc.)
        well_number = int(well[1:])  # Extract the number (1, 2, etc.)

        # Fetch the corresponding i5 value from the index
        i5_value = f"{i5_row}{well_number}"  # e.g., if i5_row is H and well is A1, this will be H1
        i5_row_data = index_df.loc[index_df['index'] == i5_value, ['i5-name', 'i5-index']].values[0]

        # Append i7 values based on the i7 column selection
        i7_value = f"{well_row}{i7_col}"  # e.g., if well is A1 and column is 12, this will be A12
        i7_row_data = index_df.loc[index_df['index'] == i7_value, ['i7-name', 'i7-index']].values[0]

        # Create a row in the output
        output_data.append({
            "Well": well,
            "i7-name": i7_row_data[0],
            "i7-index": i7_row_data[1],
            "i5-name": i5_row_data[0],
            "i5-index": i5_row_data[1]
        })

    # Create a DataFrame from the output data
    output_df = pd.DataFrame(output_data)

    # Generate timestamp in the format day_month_year_min_sec
    timestamp = datetime.datetime.now().strftime("%D_%M%S")

    # Add download button for the horizontal output
    st.download_button(
        label="Download Horizontal Output as CSV",
        data=output_df.to_csv(index=False),
        file_name=f"horizontal_output_{timestamp}.csv",
        mime="text/csv"
    )
    # Display the DataFrame in horizontal format
    st.subheader("→ Horizontal Output")
    st.write(output_df)

    # Create a DataFrame for vertical output with the specified order
    vertical_output_data = []
    rows = [f"{chr(65 + r)}{c + 1}" for c in range(12) for r in range(8)]
    
    # Populate the vertical output data using the same logic
    for well in rows:
        if well in selected_data:
            well_row = well[0]
            well_number = int(well[1:])
            
            # Fetch the corresponding i5 value from the index
            i5_value = f"{i5_row}{well_number}"
            i5_row_data = index_df.loc[index_df['index'] == i5_value, ['i5-name', 'i5-index']].values[0]
            
            # Fetch the corresponding i7 value from the index
            i7_value = f"{well_row}{i7_col}"
            i7_row_data = index_df.loc[index_df['index'] == i7_value, ['i7-name', 'i7-index']].values[0]
            
            # Append to vertical output data
            vertical_output_data.append({
                "Well": well,
                "i7-name": i7_row_data[0],
                "i7-index": i7_row_data[1],
                "i5-name": i5_row_data[0],
                "i5-index": i5_row_data[1]
            })

    # Create a DataFrame for vertical output
    vertical_output_df = pd.DataFrame(vertical_output_data)
    
    # Add download button for the vertical output
    st.download_button(
        label="Download Vertical Output as CSV",
        data=vertical_output_df.to_csv(index=False),
        file_name=f"vertical_output_{timestamp}.csv",
        mime="text/csv"
    )

    # Display the DataFrame in vertical format
    st.subheader("↓ Vertical Output")
    st.write(vertical_output_df)
