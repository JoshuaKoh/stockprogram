package com.joshuakoh.stocksolver;

public class TickerCol {

	private TickerData[] tickerCol;
	
	public TickerCol() {
		tickerCol = new TickerData[8];
	}
	
	public TickerData getId() {
		return tickerCol[0];
	}
	
	public void setId(int id) {
		tickerCol[0].setData(id);
		tickerCol[0].setUpdated(true);
	}
	
	public TickerData getDate() {
		return tickerCol[1];
	}
	
	public void setDate(int date) {
		tickerCol[1].setData(date);
		tickerCol[1].setUpdated(true);
	}
	
	public TickerData getOpen() {
		return tickerCol[2];
	}
	
	public void setOpen(int open) {
		tickerCol[2].setData(open);
		tickerCol[2].setUpdated(true);
	}
	
	public TickerData getHigh() { // 420 blaze it
		return tickerCol[3];
	}
	
	public void setHigh(int high) {
		tickerCol[3].setData(high);
		tickerCol[3].setUpdated(true);
	}
	
	public TickerData getLow() { // get low get low get low
		return tickerCol[4];
	}
	
	public void setLow(int low) {
		tickerCol[4].setData(low);
		tickerCol[4].setUpdated(true);
	}
	
	public TickerData getClose() { // to me baby
		return tickerCol[5];
	}
	
	public void setClose(int close) {
		tickerCol[5].setData(close);
		tickerCol[5].setUpdated(true);
	}
	
	public TickerData getVolume() {
		return tickerCol[6];
	}
	
	public void setVolume(int volume) { // to 11
		tickerCol[6].setData(volume);
		tickerCol[6].setUpdated(true);
	}
	
	public TickerData getAdjClose() {
		return tickerCol[7];
	}
	
	public void setAdjClose(int adj_close) {
		tickerCol[7].setData(adj_close);
		tickerCol[7].setUpdated(true);
	}
	
}
