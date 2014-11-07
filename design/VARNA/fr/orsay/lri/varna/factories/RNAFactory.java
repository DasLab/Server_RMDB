package fr.orsay.lri.varna.factories;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.io.Reader;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Hashtable;
import java.util.List;
import java.util.Vector;

import javax.xml.parsers.SAXParser;
import javax.xml.parsers.SAXParserFactory;

import org.xml.sax.InputSource;

import fr.orsay.lri.varna.exceptions.ExceptionExportFailed;
import fr.orsay.lri.varna.exceptions.ExceptionFileFormatOrSyntax;
import fr.orsay.lri.varna.exceptions.ExceptionLoadingFailed;
import fr.orsay.lri.varna.exceptions.ExceptionPermissionDenied;
import fr.orsay.lri.varna.exceptions.ExceptionUnmatchedClosingParentheses;
import fr.orsay.lri.varna.models.rna.ModeleBP;
import fr.orsay.lri.varna.models.rna.ModeleBase;
import fr.orsay.lri.varna.models.rna.RNA;
import fr.orsay.lri.varna.models.rna.RNAMLParser;

public class RNAFactory {

	public enum RNAFileType{
		FILE_TYPE_BPSEQ,
		FILE_TYPE_CT,
		FILE_TYPE_DBN,
		FILE_TYPE_RNAML,
		FILE_TYPE_UNKNOWN
	};


	public static Collection<RNA> loadSecStrRNAML(Reader r) throws ExceptionPermissionDenied,
			ExceptionLoadingFailed, ExceptionFileFormatOrSyntax {

		ArrayList<RNA> result = new ArrayList<RNA>();
		try {
			System.setProperty("javax.xml.parsers.SAXParserFactory", "com.sun.org.apache.xerces.internal.jaxp.SAXParserFactoryImpl");
			SAXParserFactory saxFact = javax.xml.parsers.SAXParserFactory.newInstance();
			saxFact.setValidating(false);
			saxFact.setXIncludeAware(false);
			saxFact.setNamespaceAware(false);
			SAXParser sp = saxFact.newSAXParser();
			RNAMLParser RNAMLData = new RNAMLParser();
			sp.parse(new InputSource(r), RNAMLData);
			
			/*XMLReader xr = XMLReaderFactory.createXMLReader();
			RNAMLParser RNAMLData = new RNAMLParser();
			xr.setContentHandler(RNAMLData);
			xr.setErrorHandler(RNAMLData);
			xr.setEntityResolver(RNAMLData);
			xr.parse(new InputSource(r));*/
			for(RNAMLParser.RNATmp rnaTmp : RNAMLData.getMolecules())
			{
				RNA current = new RNA();
				// Retrieving parsed data
				List<String> seq = rnaTmp.getSequence();
				//System.err.println(""+seq.size());
				// Creating empty structure of suitable size
				int[] str = new int[seq.size()];
				for (int i=0;i<str.length;i++)
				{ str[i] = -1; }
				current.setRNA(seq, str);
				Vector<RNAMLParser.BPTemp> allbpsTmp = rnaTmp.getStructure();
				ArrayList<ModeleBP> allbps = new ArrayList<ModeleBP>();
				for (int i = 0; i < allbpsTmp.size(); i++) {
					RNAMLParser.BPTemp bp = allbpsTmp.get(i);
					//System.err.println(bp);
					int bp5 = bp.pos5;
					int bp3 = bp.pos3;
					ModeleBase mb = current.getBaseAt(bp5);
					ModeleBase part = current.getBaseAt(bp3);
					ModeleBP newStyle = bp.createBPStyle(mb, part);
					allbps.add(newStyle);
				}

				current.applyBPs(allbps);
				result.add(current);
			}

		} catch (IOException ioe) {
			throw new ExceptionLoadingFailed(
					"Couldn't load file due to I/O or security policy issues.",
					"");
		} catch (Exception ge) {
          ge.printStackTrace();
		}

		return result;
	}

	public static Collection<RNA> loadSecStrDBN(Reader r) throws ExceptionLoadingFailed,
			ExceptionPermissionDenied, ExceptionUnmatchedClosingParentheses,
			ExceptionFileFormatOrSyntax {
		boolean loadOk = false;
		ArrayList<RNA> result = new ArrayList<RNA>();
		RNA current = new RNA();
		try {
			BufferedReader fr = new BufferedReader(r);
			String line = fr.readLine();
			String title = "";
			String seqTmp = "";
			String strTmp = "";
			while ((line != null) && (strTmp.equals(""))) {
				line = line.trim();
				if (!line.startsWith(">")) {
					if (seqTmp.equals("")) {
						seqTmp = line;
					} else {
						strTmp = line;
					}
				}
				else
				{
					title = line.substring(1).trim();
				}
				line = fr.readLine();
			}
			if (strTmp.length() != 0) {
				current.setRNA(seqTmp, strTmp);
				current.setName(title);
				loadOk = true;
			}
		} catch (IOException e) {
			throw new ExceptionLoadingFailed(e.getMessage(), "");
		}
		if ( loadOk)
		{
			result.add(current);
		}
		return result;
	}

	public static Collection<RNA> loadSecStr(Reader r) throws ExceptionFileFormatOrSyntax {
		return loadSecStr(r,RNAFileType.FILE_TYPE_UNKNOWN);
		}

	public static Collection<RNA> loadSecStr(Reader r, RNAFileType fileType) throws ExceptionFileFormatOrSyntax 
	{			
		switch(fileType)
		{		
			case FILE_TYPE_DBN:
			{
				try {
					Collection<RNA> result = loadSecStrDBN(r);
					if (result.size()!=0) return result;
				} catch (Exception e) { }
			}
			break;
			case FILE_TYPE_CT:
			{
				try {
					Collection<RNA> result = loadSecStrCT(r);
					if (result.size()!=0) return result;
				} catch (Exception e) { }
			}
			break;
			case FILE_TYPE_BPSEQ:
			{
				try {
					Collection<RNA> result = loadSecStrBPSEQ(r);
					if (result.size()!=0) return result;
				} catch (Exception e) { }
			}
			break;
			case FILE_TYPE_RNAML:
			{
				try {
					Collection<RNA> result = loadSecStrRNAML(r);
					if (result.size()!=0) return result;
				} catch (Exception e) { }
			}
			break;
			case FILE_TYPE_UNKNOWN:
			{
				BufferedReader buf = new BufferedReader(r);

				try {
					buf.mark(1000000);
					try {
						Collection<RNA> result = loadSecStrCT(buf);
						if (result.size()!=0) return result;
					} catch (Exception e) {
					}
					buf.reset();
					try {
						Collection<RNA> result = loadSecStrBPSEQ(buf);
						if (result.size()!=0) return result;
					} catch (Exception e) {
					}
					buf.reset();
					try {
						Collection<RNA> result = loadSecStrDBN(buf);
						if (result.size()!=0) return result;
					} catch (Exception e) {
						e.printStackTrace();
					}
					buf.reset();
					try {
						Collection<RNA> result = loadSecStrRNAML(buf);
						if (result.size()!=0) return result;
					} catch (ExceptionLoadingFailed e2)
					{
						e2.printStackTrace();
					} catch (Exception e) {
						e.printStackTrace();
					}
					try {
						Collection<RNA> result = loadSecStrRNAML(buf);
						if (result.size()!=0) return result;
					} catch (ExceptionLoadingFailed e2)
					{
						e2.printStackTrace();
					} catch (Exception e) {
						e.printStackTrace();
					}
					buf.reset();
				} catch (IOException e2) {
					e2.printStackTrace();
				}
			}
		}		
		throw new ExceptionFileFormatOrSyntax("");
	}

	public static RNAFileType guessFileTypeFromExtension(String path)
	{
		if (path.toLowerCase().endsWith("ml"))
		{ return RNAFileType.FILE_TYPE_RNAML; }
		else if (path.toLowerCase().endsWith("dbn")||path.toLowerCase().endsWith("faa"))
		{ return RNAFileType.FILE_TYPE_DBN; }
		else if (path.toLowerCase().endsWith("ct"))
		{ return RNAFileType.FILE_TYPE_CT; }
		else if (path.toLowerCase().endsWith("bpseq"))
		{ return RNAFileType.FILE_TYPE_BPSEQ; }
		
		return RNAFileType.FILE_TYPE_UNKNOWN; 			

	}
	
	public static Collection<RNA> loadSecStr(String path) throws ExceptionExportFailed,
			ExceptionPermissionDenied, ExceptionLoadingFailed,
			ExceptionFileFormatOrSyntax, ExceptionUnmatchedClosingParentheses,
			FileNotFoundException {
		FileReader fr = null;
		try {
			fr = new FileReader(path); 
			RNAFileType type = guessFileTypeFromExtension(path);
			return loadSecStr(fr,type);
		} catch (ExceptionFileFormatOrSyntax e) {
			if (fr != null)
				try {fr.close();} catch(IOException e2){}
			e.setPath(path);
			throw e;
		}
	}

	public static Collection<RNA> loadSecStrBPSEQ(Reader r) throws ExceptionPermissionDenied,
	ExceptionLoadingFailed, ExceptionFileFormatOrSyntax {
boolean loadOk = false;
ArrayList<RNA> result = new ArrayList<RNA>();
RNA current = new RNA();
try {
	BufferedReader fr = new BufferedReader(r);
	String line = fr.readLine();
	ArrayList<String> seqTmp = new ArrayList<String>();
	Hashtable<Integer,Vector<Integer> > strTmp = new Hashtable<Integer,Vector<Integer>>();

	int bpFrom;
	String base;
	int bpTo;
	int minIndex = -1;
	boolean noWarningYet = true;
	String title = "";
	String filenameStr = "Filename:";
	String organismStr = "Organism:";
	String ANStr = "Accession Number:";
	while (line != null) {
		line = line.trim();
		String[] tokens = line.split("\\s+");
		if ((tokens.length >= 3) && !tokens[0].contains("#")&& !line.startsWith("Organism:")&& !line.startsWith("Citation")
				 && !line.startsWith("Filename:")&& !line.startsWith("Accession Number:")) 
		{
				base = tokens[1];
				seqTmp.add(base);
				bpFrom = (Integer.parseInt(tokens[0]));
				if (minIndex<0) minIndex = bpFrom;
				
				if (seqTmp.size() < (bpFrom-minIndex+1)) {
					if (noWarningYet) {
						noWarningYet = false;
						/*warningEmition("Discontinuity detected between nucleotides "
								+ (seqTmp.size())
								+ " and "
								+ (bpFrom + 1)
								+ "!\nFilling in missing portions with unpaired unknown 'X' nucleotides ...");*/
					}
					while (seqTmp.size() < (bpFrom-minIndex+1)) {
						//System.err.println(".");
						seqTmp.add("X");								
					}
				}
				for (int i=2;i<tokens.length;i++)
				{
					bpTo = (Integer.parseInt(tokens[i]));
				  if ((bpTo!=0)||(i!=tokens.length-1))
				  {
				  if (!strTmp.containsKey(bpFrom))
				    strTmp.put(bpFrom,new Vector<Integer>());
				  strTmp.get(bpFrom).add(bpTo);
				  }
				}
		}
		else if (tokens[0].startsWith("#"))
		{
			int occur = line.indexOf("#");
			String tmp = line.substring(occur+1);
			title += tmp.trim()+" ";
		}
		else if (tokens[0].startsWith(filenameStr))
		{
			int occur = line.indexOf(filenameStr);
			String tmp = line.substring(occur+filenameStr.length());
			title += tmp.trim();
		}
		else if (tokens[0].startsWith(organismStr))
		{
			int occur = line.indexOf(organismStr);
			String tmp = line.substring(occur+organismStr.length());
			if (title.length()!=0)
			{
				title = "/"+title;
			}
			title = tmp.trim() + title;
		}
		else if (line.contains(ANStr))
		{
			int occur = line.indexOf(ANStr);
			String tmp = line.substring(occur+ANStr.length());
			if (title.length()!=0)
			{
				title += " ";
			}
			title +="("+tmp.trim()+")";
		}
		line = fr.readLine();
	}
	if (strTmp.size() != 0) {
		ArrayList<String> seq = seqTmp;
		int[] str = new int[seq.size()];
		for (int i = 0; i < seq.size(); i++) {
			str[i] = -1;
		}
		current.setRNA(seq, str, minIndex);
		ArrayList<ModeleBP> allbps = new ArrayList<ModeleBP>();
		for (int i:strTmp.keySet()) 
		{
			for (int j: strTmp.get(i))
			{
				ModeleBase mb = current.getBaseAt(i-minIndex);
				ModeleBase part = current.getBaseAt(j-minIndex);
				ModeleBP newStyle = new ModeleBP(mb, part);
				allbps.add(newStyle);						
			}
		}
		current.applyBPs(allbps);
		current.setName(title);
		loadOk = true;
	}
}
catch (NumberFormatException e) {
	e.printStackTrace();
} catch (IOException e) {
	// TODO Auto-generated catch block
	e.printStackTrace();
}
catch (Exception e) {
	throw new ExceptionLoadingFailed(e.getMessage(), "");
} 
if (loadOk) 
	result.add(current);
return result;
}

public static Collection<RNA> loadSecStrCT(Reader r) throws ExceptionPermissionDenied,
	ExceptionLoadingFailed, ExceptionFileFormatOrSyntax {
boolean loadOk = false;
ArrayList<RNA> result = new ArrayList<RNA>();
RNA current = new RNA();
try {
	BufferedReader fr = new BufferedReader(r);
	String line = fr.readLine();
	ArrayList<String> seq = new ArrayList<String>();
	Vector<Integer> strTmp = new Vector<Integer>();
	int bpFrom;
	String base;
	int bpTo;
	boolean noWarningYet = true;
	int minIndex = -1;
	String title = "";
	while (line != null) 
	{
		line = line.trim();
		String[] tokens = line.split("\\s+");
		if (tokens.length >= 6) {
			try{
			bpFrom = (Integer.parseInt(tokens[0]));
			bpTo = (Integer.parseInt(tokens[4]));
			if (minIndex==-1)
				minIndex = bpFrom;
			bpFrom -= minIndex;
			if (bpTo!=0)
				bpTo -= minIndex;
			else
				bpTo = -1;
			base = tokens[1];
			Integer.parseInt(tokens[2]);
			Integer.parseInt(tokens[3]);
			Integer.parseInt(tokens[5]);
			if (bpFrom != seq.size()) {
				if (noWarningYet) {
					noWarningYet = false;
					/*warningEmition("Discontinuity detected between nucleotides "
							+ (seq.size())
							+ " and "
							+ (bpFrom + 1)
							+ "!\nFilling in missing portions with unpaired unknown 'X' nucleotides ...");*/
				}
				while (bpFrom > seq.size()) {
					seq.add("X");
					strTmp.add(-1);
				}
			}
			seq.add(base);
			strTmp.add(bpTo);
			}
			catch (NumberFormatException e) {
				}
		}
		if ((line.contains("ENERGY = "))||line.contains("dG = ")) 
		{
			String[] ntokens = line.split("\\s+");
			if (ntokens.length>=4)
			{
				String energy = ntokens[3];
				for(int i=4;i<ntokens.length;i++)
				{
					title += ntokens[i]+" ";
				}
				title += "(E="+energy+" kcal/mol)";
			}
		}
		line = fr.readLine();
	}
	if (strTmp.size() != 0) {
		int[] str = new int[strTmp.size()];
		for (int i = 0; i < strTmp.size(); i++) {
			str[i] = strTmp.elementAt(i).intValue();
		}
		current.setRNA(seq, str, minIndex);
		current.setName(title);
		loadOk = true;
	}
} catch (IOException e) {
	throw new ExceptionLoadingFailed(e.getMessage(), "");
} catch (NumberFormatException e) {
	throw new ExceptionFileFormatOrSyntax(e.getMessage(), "");
}
if (loadOk) 
	result.add(current);
return result;
}
	
	
}
