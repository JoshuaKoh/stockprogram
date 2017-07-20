package com.joshuakoh.stocksolver;

public class DbFunctions {

	private static final String TABLE = "tickers";
	private static final String COL_ID = "id";
	private static final String COL_DATE = "date";
	private static final String COL_OPEN = "open";
	private static final String COL_HIGH = "high";
	private static final String COL_LOW = "low";
	private static final String COL_CLOSE = "close";
	private static final String COL_VOLUME = "volume";
	private static final String COL_ADJ_CLOSE = "adj_close";
	private static final String COMMA = ", ";
	/*
	 * COL_ID + COMMA + COL_DATE + COMMA +
				COL_OPEN + COMMA + COL_HIGH + COMMA + COL_LOW + COMMA + COL_CLOSE + 
				COL_VOLUME + COMMA + COL_ADJ_CLOSE
	 */
	private int id;
	private int date;
	private int open;
	private int high;
	private int low;
	private int close;
	private int volume;
	private int adj_close;
	
	public void add(TickerCol tc) {
		String update = "INSERT INTO " + TABLE + " VALUES (" + tc. +
	}
	
	
}
