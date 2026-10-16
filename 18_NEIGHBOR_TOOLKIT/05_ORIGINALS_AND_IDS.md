# Keep every record connected to its original

A record is easier to verify when nobody has to guess which picture, message or document it came from. Use a **small, repeatable ID system**, not a complicated evidence database.

| Prefix | Used for | Example |
| --- | --- | --- |
| `E` | Event or observation | `E-001` |
| `P` | Photo, video or other captured media | `P-001` |
| `F` | Individual drainage feature or safe map point | `F-001` |
| `R` | Official document or other received record | `R-001` |
| `C` | Contact, request, reply or meeting | `C-001` |
| `W` | Work activity, repair or condition change | `W-001` |
| `H` | Private household/property-condition entry | `H-001` |

**Assign IDs within one household's private folder.** Different neighbors may both have an `E-001`; identify the household privately when combining material. Never reuse an ID for a different item. If a row changes, keep the earlier dated entry and add a correction referencing the same item.

## Basic protected folder layout (example only)

```text
My_Tom_Street_Records/
  01_ORIGINAL_FILES/        [unchanged camera or agency files]
  02_COMPLETED_FORMS/       [private scanned pages or filled-in logs]
  03_SHARE_COPIES/          [separately labeled approved copies]
  04_REQUESTS_AND_REPLIES/  [sent messages, receipts, responses]
  05_INDEX/                 [file IDs and backup notes]
```

Save originals to at least one backup location you control. Keep the exact original filename in your index; descriptive filenames may be assigned to **copies**. Log a transfer when another person receives material: what was shared, by whom, when and how, whether it was the original or a copy, and any limitations. Avoid putting personal file paths into a public document.

**Optional hash:** A SHA-256 value is a fingerprint of the bytes of a particular file. It can help check that a later copy matches the earlier one. It does **not** certify where, when or by whom a photograph was taken. If you don't know how to calculate one, leave the field blank instead of inventing a value.

**For a photograph**, log the source/camera or private reference, capture date/time and time zone (or unknown), direction/viewpoint, related event ID, exact filename, stored original and any edit-copy ID. **For an official record**, log the issuing office, document number, date issued, date retrieved, revision/page, original filename and related permit or feature.

Use the [photo and file worksheet](print/04_Photo_and_Video_Index.pdf), [original handoff worksheet](print/14_Original_Files_and_Handoff.pdf) or blank [media CSV](templates/PHOTO_VIDEO_INDEX.csv) and [custody CSV](templates/ORIGINAL_FILE_AND_TRANSFER_LOG.csv). Completed versions stay private.
