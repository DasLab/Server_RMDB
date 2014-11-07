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

import java.awt.geom.Point2D;

public class LineCommand extends GraphicElement {
	private Point2D.Double _orig;
	private Point2D.Double _dest;
	private double _thickness;

	public LineCommand(Point2D.Double orig, Point2D.Double dest,
			double thickness) {
		_orig = orig;
		_dest = dest;
		_thickness = thickness;
	}

	public Point2D.Double get_orig() {
		return _orig;
	}

	public Point2D.Double get_dest() {
		return _dest;
	}

	public double get_thickness() {
		return _thickness;
	}
}
