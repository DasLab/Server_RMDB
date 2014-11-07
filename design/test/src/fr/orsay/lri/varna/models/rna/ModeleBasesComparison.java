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
package fr.orsay.lri.varna.models.rna;

import java.awt.Color;
import java.awt.geom.Point2D;


/**
 * <b>The RNA base comparison model</b>. In each bases we'll place <b>two
 * characters</b> representing nitrogenous bases of both RNA that have to be
 * compared. So, in each base in the comparison model, we'll have a <b>couple of
 * bases</b>, with the same coordinates on the final drawing.
 * 
 * @author Masson
 * 
 */
public class ModeleBasesComparison extends ModeleBase {

	/*
	 * LOCAL FIELDS
	 */

	/**
	 * 
	 */
	private static final long serialVersionUID = -2733063250714562463L;

	/**
	 * The base of the first RNA associated with the base of the second RNA.
	 */
	private Character _base1;

	/**
	 * The base of the second RNA associated with the base of the first RNA.
	 */
	private Character _base2;

	/**
	 * This ModeleBasesComparison owning statement. It's value will be 0 if this
	 * base is common for both RNA that had been compared, 1 if this base is
	 * related to the first RNA, 2 if related to the second. Default is -1.
	 */
	private int _appartenance = -1;

	/**
	 * This base's offset in the sequence
	 */
	private int _index;

	/*
	 * -> END LOCAL FIELDS <--
	 */

	public static Color FIRST_RNA_COLOR = Color.decode("#FFDD99");
	public static Color SECOND_RNA_COLOR = Color.decode("#99DDFF");
	public static Color BOTH_RNA_COLOR = Color.decode("#99DD99");
	public static Color DEFAULT_RNA_COLOR = Color.white;

	/*
	 * CONSTRUCTORS
	 */

	/**
	 * Creates a new comparison base with the default display style and no
	 * nitrogenous bases.
	 */
	public ModeleBasesComparison(int index) {
		this(' ', ' ', index);
	}

	/**
	 * Creates a new comparison base at the specified coordinates, with the
	 * default display style and no nitrogenous bases.
	 * 
	 * @param coords
	 *            - The coordinates in which the comparison base has to be
	 *            placed.
	 */
	public ModeleBasesComparison(Point2D coords, int index) {
		this(' ', ' ', new Point2D.Double(coords.getX(), coords.getY()), index);
	}

	/**
	 * Creates a new comparison base with the specified nitrogenous bases.
	 * 
	 * @param base1
	 *            - The first RNA' nitrogenous base
	 * @param base2
	 *            - The second RNA' nitrogenous base
	 */
	public ModeleBasesComparison(char base1, char base2, int index) {
		this(base1, base2, -1, index);
	}

	/**
	 * Creates a new comparison base with the specified nitrogenous bases, at
	 * the specified coordinates.
	 * 
	 * @param base1
	 *            - The first RNA' nitrogenous base
	 * @param base2
	 *            - The second RNA' nitrogenous base
	 * @param coords
	 *            - The coordinates in which the comparison base has to be
	 *            placed.
	 */
	public ModeleBasesComparison(char base1, char base2, Point2D coords,
			int index) {
		this(new Point2D.Double(coords.getX(), coords.getY()), base1, base2,
				true, new ModeleStyleBase(), -1, index);
	}

	/**
	 * Creates a new comparison base with the specified nitrogenous bases.
	 * 
	 * @param base1
	 *            - The first RNA' nitrogenous base
	 * @param base2
	 *            - The second RNA' nitrogenous base
	 */
	public ModeleBasesComparison(char base1, char base2, int elementStructure,
			int index) {
		this(new Point2D.Double(), base1, base2, true, new ModeleStyleBase(),
				elementStructure, index);
	}

	/**
	 * Creates a new comparison base with the specified nitrogenous bases.
	 * 
	 * @param coords
	 *            - This base's XY coordinates
	 * @param base1
	 *            - The first RNA' nitrogenous base
	 * @param base2
	 *            - The second RNA' nitrogenous base
	 * @param colorie
	 *            - Whether or not this base will be drawn
	 * @param mb
	 *            - The drawing style for this base
	 * @param elementStructure
	 *            - The index of a bp partner in the secondary structure
	 * @param index
	 *            - Index of this base in its initial sequence
	 */
	public ModeleBasesComparison(Point2D coords, char base1, char base2,
			boolean colorie, ModeleStyleBase mb, int elementStructure, int index) {
		_colorie = colorie;
		_base1 = base1;
		_base2 = base2;
		_styleBase = mb;
		_coords = new VARNAPoint(coords.getX(), coords.getY());
		_elementStructure = elementStructure;
		_index = index;
	}

	/*
	 * -> END CONSTRUCTORS <--
	 */

	/*
	 * GETTERS & SETTERS
	 */

	/**
	 * Return the display style associated to this comparison base.
	 * 
	 * @return The display style associated to this comparison base.
	 */
	public ModeleStyleBase getStyleBase() {
		if (_colorie)
			return _styleBase;
		return new ModeleStyleBase();
	}

	/**
	 * Allows to know if this comparison base is colored.
	 * 
	 * @return TRUE if this comparison base is colored, else FALSE.
	 */
	public Boolean get_colored() {
		return _colorie;
	}

	/**
	 * Sets the coloration authorization of this comparison base.
	 * 
	 * @param colored
	 *            - TRUE if this comparison base has to be colored, else FALSE.
	 */
	public void set_colored(Boolean colored) {
		this._colorie = colored;
	}


	/**
	 * Return the base of the first RNA in this comparison base.
	 * 
	 * @return The base of the first RNA in this comparison base.
	 */
	public Character get_base1() {
		return _base1;
	}

	/**
	 * Sets the base of the first RNA in this comparison base.
	 * 
	 * @param _base1
	 *            - The base of the first RNA in this comparison base.
	 */
	public void set_base1(Character _base1) {
		this._base1 = _base1;
	}

	/**
	 * Return the base of the second RNA in this comparison base.
	 * 
	 * @return The base of the second RNA in this comparison base.
	 */
	public Character get_base2() {
		return _base2;
	}

	/**
	 * Sets the base of the second RNA in this comparison base.
	 * 
	 * @param _base2
	 *            - The base of the second RNA in this comparison base.
	 */
	public void set_base2(Character _base2) {
		this._base2 = _base2;
	}

	/*
	 * --> END GETTERS & SETTERS <--
	 */

	/**
	 * Gets the string representation of the two bases in this
	 * ModeleBasesComparison.
	 * 
	 * @return the string representation of the two bases in this
	 *         ModeleBasesComparison.
	 */
	public String getBases() {
		return String.valueOf(_base1) + String.valueOf(_base2);
	}

	public String getContent() {
		return getBases();
	}

	/**
	 * Gets this InterfaceBase assiociated structure element.
	 * 
	 * @return this InterfaceBase assiociated structure element.
	 */
	public int getElementStructure() {
		return _elementStructure;
	}

	/**
	 * Sets this InterfaceBase assiociated structure element.
	 * 
	 * @param structure
	 *            - This new assiociated structure element.
	 */
	public void setElementStructure(int structure) {
		_elementStructure = structure;
	}

	/**
	 * Gets this base's related RNA.
	 * 
	 * @return 0 if this base is common for both RNA<br>
	 *         1 if this base is related to the first RNA<br>
	 *         2 if this base is related to the second RNA
	 */
	public int get_appartenance() {
		return _appartenance;
	}

	/**
	 * Sets this base's related RNA.
	 * 
	 * @param _appartenance
	 *            : 0 if this base is common for both RNA<br>
	 *            1 if this base is related to the first RNA<br>
	 *            2 if this base is related to the second RNA.
	 */
	public void set_appartenance(int _appartenance) {
		if (_appartenance == 0) {
			this.getStyleBase().set_base_inner_color(BOTH_RNA_COLOR);
		} else if (_appartenance == 1) {
			this.getStyleBase().set_base_inner_color(FIRST_RNA_COLOR);
		} else if (_appartenance == 2) {
			this.getStyleBase().set_base_inner_color(SECOND_RNA_COLOR);
		} else {
			this.getStyleBase().set_base_inner_color(DEFAULT_RNA_COLOR);
		}
		this._appartenance = _appartenance;
	}

	public Boolean getColorie() {
		return _colorie;
	}

	public void setColorie(Boolean _colorie) {
		this._colorie = _colorie;
	}

	public int getIndex() {
		return _index;
	}

	@Override
	public void setContent(String s) {
		this.set_base1(s.charAt(0));
		this.set_base2(s.charAt(1));
	}

}
