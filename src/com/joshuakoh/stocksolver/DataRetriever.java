package com.joshuakoh.stocksolver;

import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.DataInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLConnection;
import java.time.DayOfWeek;
import java.time.LocalDate;

public class DataRetriever {
	private URL url;
	private URLConnection urlc;
	private String content;
	
	public DataRetriever() {
		
	}
	
	public void run() {
		updateStocks();
		commitData(content);
	}
	
	public void updateStocks() {
		// Iterate through stock tickers and perform this on all
		String ticker = "GE"; // TODO temporary implementation
		int timespan = 7; // in days TODO temp
		
		LocalDate lastDate = LocalDate.now();
		LocalDate startDate = LocalDate.now();
		LocalDate[] invalidDays = {}; // TODO fill in, stores holidays and non-weekend off-days
		for (int i = 0; i < timespan; i++) {
			if (startDate.getDayOfWeek() == DayOfWeek.SUNDAY) { // Skips weekends
				startDate = startDate.minusDays(2);
			}
			for (int j = 0; j < invalidDays.length; j++) { // Skips invalid days
				if (startDate == invalidDays[j]) {
					startDate = startDate.minusDays(1);
				}
			}
			startDate = startDate.minusDays(1);
		}
		int startMonth = startDate.getMonthValue();
		int startDay = startDate.getDayOfMonth();
		int startYear = startDate.getYear();
		int lastMonth = lastDate.getMonthValue();
		int lastDay = lastDate.getDayOfMonth();
		int lastYear = lastDate.getYear();
		
		// Forms URL based on Yahoo's URL structure
		String tempURL = "http://real-chart.finance.yahoo.com/table.csv?s=" + 
				ticker +
				"&a=" + (startMonth - 1) +
				"&b=" + startDay + 
				"&c=" + startYear +
				"&d=" + (lastMonth - 1) +
				"&e=" + lastDay +
				"&f=" + lastYear + 
				"&g=d&ignore=.csv";
		setURL(tempURL);
		
		try {
			urlc = url.openConnection();
			content = retrieveData(urlc, 
					new BufferedReader(new InputStreamReader(urlc.getInputStream())),
					new StringBuilder());
		} catch (IOException e) {
			System.out.println("Error - Could not retrieve data from Yahoo! Possible causes include:"
					+ "\n- You may not be connected to the internet."
					+ "\n- Program tried to connect with a bad URL."
					+ "\n- InputStream could not be established.");
			e.printStackTrace();
			System.exit(1);
		}
	}
	
	public void setURL(String link) {
		try {
			url = new URL(link);
		} catch (MalformedURLException e) {
			System.out.println("Error - URL in setURL() was not formatted correctly!");
			System.exit(1);
		}
	}
	
	public String retrieveData(URLConnection urlc, BufferedReader br, StringBuilder contentSB) {
		try {
			String readLine;
			while ((readLine = br.readLine()) != null) {
		        contentSB.append(readLine + "\n");
		    }
		    br.close();
		} catch (IOException e) {
			System.out.println("Error - Line in retrieveData() could not be read!");
			System.exit(1);
		}
		return contentSB.toString();
	}
	
	private void commitData(String content) {
		String[] lines = content.split("\\r?\\n");
		for (int i = 1; i < lines.length; i++) { // Starts at 1 to skip header line
			String[] data = lines[i].split("[,]");
			/* TODO
			 * At data[0] (date) in mySQL data table, add each data element data[1... n].
			 * Date,Open,High,Low,Close,Volume,Adj Close
			 */
		}
	}
}
