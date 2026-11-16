# Fonts

`ElowaKR-subset.woff2` is a subset of **Pretendard Variable 1.3.9** by Kil
Hyung-jin (https://github.com/orioncactus/pretendard), licensed under the SIL
Open Font License 1.1 (`LICENSE-OFL.txt`). Because "Pretendard" is a Reserved
Font Name under that license, the subset is renamed "Elowa KR".

It keeps the 2,350 common Hangul syllables (KS X 1001), compatibility jamo,
Latin-1, and common punctuation, at weights 100–900. Characters outside it fall
back to the system font. It is used for Korean pages only (`:lang(ko)`).

Rebuild from the release zip (`web/variable/woff2/PretendardVariable.woff2`)
with fontTools: `pyftsubset … --text-file=<chars> --layout-features='*'
--flavor=woff2`, then rename the name-table entries.
