package com.joshuakoh.stocksolver;

public class TickerData {
	private int data;
	private boolean isUpdated;
	
	public TickerData(int data, boolean isUpdated) {
		this.data = data;
		this.isUpdated = isUpdated;
	}

	public int getData() {
		return data;
	}

	public void setData(int data) {
		this.data = data;
	}

	public boolean isUpdated() {
		return isUpdated;
	}

	public void setUpdated(boolean isUpdated) {
		this.isUpdated = isUpdated;
	}
	
	
}
