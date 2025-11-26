import pandas as pd
import logging
import config


logger = logging.getLogger(__name__)

def select_meta_cols(input_path, output_path='tmp//selected_combined_meta_cols.csv', create_csv:bool = False):
    '''
    Erstelle eine neues Dataframe aus CSV mit Metadaten, dabei werden nur notwendige Spalten uebernommen:
    id, parent, Parent1, Parent2,.., Parent13
    :param input_path:
    :param [optional] output_path:
    :param create_csv:
    :return: path to new csv file (with prepared data)
    '''

    logger.info(f"select_meta_cols: Reading csv {input_path} ...")
    meta_df = pd.read_csv(input_path, sep=';', dtype=str)
    input_rows = len(meta_df)

    parent_cols = [col for col in meta_df.columns if "Parent" in col and col != "Parent1"]

    # Wähle die Spalten aus
    cols_to_use = ['id', 'filename', 'parent'] + parent_cols
    new_df = meta_df[cols_to_use].copy()

    # Alle zu reinigenden Spalten (außer id) zusammen
    cols_to_clean = new_df.columns.drop('id')  # alles außer 'id'

    # Reinigung: Tabs, Quotes, NaN, (12345), doppelte Leerzeichen
    new_df[cols_to_clean] = new_df[cols_to_clean].astype(str).apply(
        lambda s: (
            s.str.replace(r'\(\d+\)\s*', '', regex=True)  # (12345)
            .str.replace(r'\b(nan|NaN|None)\b', '', regex=True)  # nan / None
            .str.replace(r'[\t"]+', '', regex=True)  # Tabs + Quotes
            .str.replace(r'\s+', ' ', regex=True)  # doppelte Leerzeichen
            .str.strip()  # trim
        )
    )

    logger.info("Combining columns after id column.")
    # Combine alle Spalten außer 'id' sauber
    new_df['combined'] = new_df[cols_to_clean].apply(
        lambda row: ' '.join([x for x in row if x.strip() != ""]), axis=1
    )

    # join first col and combined col
    first_col = new_df.columns[0]
    combined_df = new_df[[first_col, "combined"]]

    #output
    output_rows = len(combined_df)
    # compare amount of rows
    if input_rows == output_rows:
        logger.info(f"OK: Amount of output rows ({output_rows}) in = amount input rows ({input_rows})")
    else:
        logger.warning(f"Warning: Amount of output rows ({output_rows}) not equal to input rows ({input_rows})!")

    #create csv it activated
    if create_csv:
        combined_df.to_csv(output_path, index=False, escapechar='\\', quoting=None)

    return output_path



if __name__ == "__main__":
    input_file = "data//dla_short_test.csv"

    df = select_meta_cols(input_file, create_csv=True)
    print(f"Successfully transformed file")