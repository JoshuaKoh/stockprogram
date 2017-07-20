package com.joshuakoh.stocksolver;

import java.sql.Connection;

import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

public class DbConnector {

	private final String URL = "jdbc:mysql://localhost:3306/stockinfo";
	private final String USERNAME = "java";
	private final String PASSWORD = "password";
	
	public DbConnector() {
		
	}
	
	public Connection connectToDb() throws SQLException {
		try {
			Class.forName("com.mysql.jdbc.Driver");
		} catch (ClassNotFoundException e) {
			// TODO Auto-generated catch block
			System.out.println("Was bad");
		}
	    	System.out.println("Connecting database...");
    		Connection conn = DriverManager.getConnection(URL, USERNAME, PASSWORD);
	    	System.out.println("Database connected!");
	    	
	    	return conn;
	    	
	}
	
	public void viewTable() throws SQLException {
		Connection con = connectToDb();
		Statement s = null;
		ResultSet rs = null;
		String query = "SELECT ticker_id, ticker FROM tickers";
		s = con.createStatement();
		rs = s.executeQuery(query);
		while (rs.next()) {
			int ticker_id = rs.getInt("ticker_id");
			String ticker = rs.getString("ticker");
			System.out.println(ticker + " - " + ticker_id);
		}
		if (s != null) {
			s.close();
		}
		if (rs != null) {
			rs.close();
		}
		if (con != null) {
			con.close();
		}
	}
	
//	public static void main(String[] args) {
//		DbConnector dbc = new DbConnector();
//		try {
//			dbc.viewTable();
//		} catch (SQLException e) {
//			System.out.println("TERMINAL ERROR: COULD NOT CONNECT TO DB!");
//			System.out.println("Failed to create statement.");
//    	    		System.exit(0);
//		}
//	}
    
    
}