/*
 VARNA is a tool for the automated drawing, visualization and annotation of the secondary structure of RNA, designed as a companion software for web servers and databases.
 Copyright (C) 2008  Kevin Darty, Alain Denise and Yann Ponty.
 electronic mail : Yann.Ponty@lri.fr
 paper mail : LRI, bat 490 Universit� Paris-Sud 91405 Orsay Cedex France

 This file is part of VARNA version 3.1.
 VARNA version 3.1 is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
 as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

 VARNA version 3.1 is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
 without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 See the GNU General Public License for more details.

 You should have received a copy of the GNU General Public License along with VARNA version 3.1.
 If not, see http://www.gnu.org/licenses.
 */
package fr.orsay.lri.varna.models.export;

import java.awt.Color;
import java.awt.geom.Point2D;
import java.awt.geom.Rectangle2D;
import java.awt.geom.Point2D.Double;

public class SVGExport extends SecStrDrawingProducer {

	private double _fontsize = 10.0;
	private Rectangle2D.Double _bb = new Rectangle2D.Double(0, 0, 10, 10);
	double _thickness = 2.0;
	
	
	public SVGExport()
	{
		super();
		super.setScale(0.5);
	}

	private String getRGBString(Color col) {
		int rpc = (int) ((((double) col.getRed()) / 255.0) * 100);
		int gpc = (int) ((((double) col.getGreen()) / 255.0) * 100);
		int bpc = (int) ((((double) col.getBlue()) / 255.0) * 100);
		return "rgb(" + rpc + "%, " + gpc + "%, " + bpc + "%)";
	}

	public String drawCircleS(Point2D.Double base, double radius,
			double thickness) {
		_thickness = thickness;
		return "<circle cx=\"" + base.x + "\" cy=\"" + (_bb.height - base.y)
				+ "\" r=\"" + radius + "\" stroke=\"" + getRGBString(_curColor)
				+ "\" stroke-width=\"" + thickness + "\" fill=\"none\"/>\n";
	}

	public String drawLineS(Point2D.Double orig, Point2D.Double dest,
			double thickness) {
		_thickness = thickness;
		return "<line x1=\"" + orig.x + "\" y1=\"" + (_bb.height - orig.y)
				+ "\" x2=\"" + dest.x + "\" y2=\"" + (_bb.height - dest.y)
				+ "\" stroke=\"" + getRGBString(_curColor)
				+ "\" stroke-width=\"" + thickness + "\" />\n";
	}

	public String drawRectangleS(Point2D.Double orig, Point2D.Double dims,
			double thickness) {
		_thickness = thickness;
		// TODO Auto-generated method stub
		return "";
	}

	public String drawTextS(Point2D.Double base, String txt) {
		//System.out.println(txt);
		return "<text x=\""
				+ (base.x)
				+ "\" y=\""
				+ (_bb.height - base.y + 0.4 * _fontsize)
				+ "\" text-anchor=\"middle\" font-family=\"Verdana\" font-size=\""
				+ _fontsize + "\" fill=\"" + getRGBString(_curColor) + "\" >"
				+ txt + "</text>\n";
	}

	public String fillCircleS(Point2D.Double base, double radius,
			double thickness, Color col) {
		_thickness = thickness;

		return "<circle cx=\"" + base.x + "\" cy=\"" + (_bb.height - base.y)
				+ "\" r=\"" + radius + "\" stroke=\"none\" stroke-width=\""
				+ thickness + "\" fill=\"" + getRGBString(col) + "\"/>\n";
	}

	public String footerS() {
		return "</svg>\n";
	}

	public String headerS(Rectangle2D.Double bb) {
		_bb = bb;
		return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
				+ "<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\" \n"
				+ "\"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">\n"
				+ "\n"
				+ "<svg width=\"100%\" height=\"100%\" version=\"1.1\"\n"
				+ "xmlns=\"http://www.w3.org/2000/svg\">\n";
	}

	public String setFontS(int font, double size) {
		_fontsize = 0.5 * size;
		return "";
	}

	public String drawArcS(Point2D.Double o, double width, double height,
			double startAngle, double endAngle) {
		// TODO: This hack assumes a (0,180) type of angle. Needs to be
		// corrected for further usage.
		double rx = width / 2.0;
		double ry = height / 2.0;
		double xs = o.x;
		double ys = (_bb.height - o.y);
		double xe = o.x + width;
		double ye = (_bb.height - o.y);

		String d = "<path d=\"M " + xs + "," + ys + " A " + rx + "," + ry
				+ " 0 0,1 " + xe + "," + ye + "\" style=\"fill:none; stroke:"
				+ getRGBString(_curColor) + "; stroke-width:" + _thickness
				+ "\"/>\n";
		return d;
	}

	public String drawPolygonS(Double[] points, double thickness) {
		String result = "<path d=\"";
		for (int i = 0; i < points.length; i++) {
			if (i == 0) {
				result += "M " + points[i].x + " " + (_bb.height - points[i].y)
						+ " ";
			} else {
				result += "L " + points[i].x + " " + (_bb.height - points[i].y)
						+ " ";
			}
		}
		result += "z\" style=\"fill:none; stroke:" + getRGBString(_curColor)
				+ "; stroke-width:" + thickness + ";\"/>\n";
		return result;
	}

	@Override
	public String fillPolygonS(Double[] points, Color col) {
		String result = "<path d=\"";
		for (int i = 0; i < points.length; i++) {
			if (i == 0) {
				result += "M " + points[i].x + " " + (_bb.height - points[i].y)
						+ " ";
			} else {
				result += "L " + points[i].x + " " + (_bb.height - points[i].y)
						+ " ";
			}
		}
		result += "z\" style=\"fill:" + getRGBString(_curColor)
				+ "; stroke:none;\"/>\n";
		return result;
	}
}
