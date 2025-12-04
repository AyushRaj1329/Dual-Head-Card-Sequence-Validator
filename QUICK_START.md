# Quick Start Guide - Auto-Detection Feature

## 🚀 What's New?

Your application now **automatically detects** card types from your files!
- **Single Card**: 1 QR code per card
- **Half Card**: 2 QR codes per card (Left/Right)
- **Quarter Card**: 4 QR codes per card - *Coming Soon*

## 📋 Quick Start

### 1. Start the Application
```bash
python main.py
```
**No dialogs, no questions** - just starts!

### 2. Load Your File
The application will **automatically detect** the card type:

**Single Card CSV:**
```csv
NUMCARD,QR
Card_001,QR1234567890
```
→ Detects: **Single Card** (1 QR field)

**Half Card CSV:**
```csv
NUMCARD,ICCID,IMSI
Card_001,ICCID123,IMSI456
```
→ Detects: **Half Card** (2 QR fields)

### 3. See the Magic! ✨
- Message shows: **"Loaded 10 cards. Detected type: Single Card"**
- UI automatically adapts to show correct number of QR fields
- Preview shows appropriate columns

### 4. Start Scanning
Everything works automatically!

## 🧪 Test It Out

We've included test files:
- `test_single_card.csv` - Try Single Card mode
- `test_half_card.csv` - Try Half Card mode

## 💡 Key Points

1. **No manual selection** - Card type detected automatically
2. **Just load your file** - Application figures out the rest
3. **UI adapts instantly** - Shows correct number of QR fields
4. **Switch anytime** - Load different file types in same session
5. **Smart detection** - Analyzes file structure intelligently

## 🔄 Switching Card Types

**It's automatic!**
1. Load a Single Card file → UI shows 1 QR field
2. Load a Half Card file → UI shows 2 QR fields
3. No restart needed!

## ❓ How Does It Know?

The application analyzes your file headers:
- **Single Card**: 2 columns (NUMCARD + QR)
- **Half Card**: 3 columns (NUMCARD + ICCID + IMSI)
- **Quarter Card**: 5 columns (NUMCARD + TL + TR + BL + BR)

## 📖 More Information

- **Detailed Testing**: See `SINGLE_CARD_TESTING_GUIDE.md`
- **Implementation Details**: See `IMPLEMENTATION_SUMMARY.md`
- **Full Plan**: See `CARD_TYPE_IMPLEMENTATION_PLAN.md`

## ✅ What Works Now

- ✅ Single Card - Fully functional
- ✅ Half Card - Fully functional (existing system)
- ⏳ Quarter Card - Coming soon

## 🐛 Troubleshooting

**Problem**: "Card not found in file"
- **Solution**: Verify QR code format matches file exactly

**Problem**: Wrong number of QR fields shown
- **Solution**: Check file has correct column headers (NUMCARD, QR/ICCID/IMSI)

**Problem**: Detection defaults to Half Card
- **Solution**: Ensure file headers match expected patterns (see AUTO_DETECTION_GUIDE.md)

## 🎯 That's It!

You're ready to use the new card type system. Start with the test files to see how it works, then use your own files.

Happy scanning! 🎉
